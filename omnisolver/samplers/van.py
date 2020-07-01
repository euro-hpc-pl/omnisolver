import dimod
import torch
import torch.nn as nn
import time
import numpy as np
from functools import partial
import random
import math
import pickle
import sys

default_dtype_torch = torch.float32


class VanSampler(dimod.Sampler):
    """Implementatoin of simple random-sampler."""

    def __init__(self, **kwargs):
        d = kwargs.pop("cuda")
        self.device = "cuda:{}".format(d) if d >= 0 else "cpu"
        self.net_params = {
            "net_depth": kwargs.pop("net_depth"),
            "net_width": kwargs.pop("net_width"),
            "bias": kwargs.pop("bias", False),
            "z2": kwargs.pop("z2", False),
            "res_block": kwargs.pop("res_block", False),
            "x_hat_clip": kwargs.pop("x_hat_clip"),
            "epsilon": kwargs.pop("epsilon"),
            "device": self.device,
        }
        if len(kwargs) > 0:
            raise ValueError("Unknown arguments: {}".format(", ".join(kwargs.keys())))

    def _prepare_sampling(self, bqm, **kwargs):
        self.ham = ModifiedSKModel(bqm.num_variables, self.device, bqm)
        self.ham.J.requires_grad = False
        net_params = dict(self.net_params)
        net_params["n"] = bqm.num_variables
        self.net = MADE(**net_params)
        self.net.to(self.device)

    def my_log(self, s):
        # if self.out_filename:
        #     with open(self.out_filename + ".log", "a", newline="\n") as f:
        #         f.write(s + u"\n")
        # if not self.no_stdout:
        #     print(s)
        print(s)

    def sample(self, bqm, **kwargs):
        start_time = time.time()
        print(bqm.num_variables)
        self._prepare_sampling(bqm)
        self.__dict__.update(kwargs)
        params = list(self.net.parameters())
        params = list(filter(lambda p: p.requires_grad, params))
        nparams = int(sum([np.prod(p.shape) for p in params]))
        self.my_log("Total number of trainable parameters: {}".format(nparams))

        if self.optimizer == "sgd":
            optimizer = torch.optim.SGD(params, lr=self.lr)
        elif self.optimizer == "sgdm":
            optimizer = torch.optim.SGD(params, lr=self.lr, momentum=0.9)
        elif self.optimizer == "rmsprop":
            optimizer = torch.optim.RMSprop(params, lr=self.lr, alpha=0.99)
        elif self.optimizer == "adam":
            optimizer = torch.optim.Adam(params, lr=self.lr, betas=(0.9, 0.999))
        elif self.optimizer == "adam0.5":
            optimizer = torch.optim.Adam(params, lr=self.lr, betas=(0.5, 0.999))
        else:
            raise ValueError("Unknown optimizer: {}".format(self.optimizer))

        init_time = time.time() - start_time
        self.my_log("init_time = {:.3f}".format(init_time))

        self.my_log("Training...")
        sample_time = 0
        train_time = 0
        start_time = time.time()
        if self.beta_anneal_to < self.beta:
            self.beta_anneal_to = self.beta
        beta = self.beta
        while beta <= self.beta_anneal_to:
            for step in range(self.max_step):
                optimizer.zero_grad()

                sample_start_time = time.time()
                with torch.no_grad():
                    sample, x_hat = self.net.sample(self.batch_size)
                assert not sample.requires_grad
                assert not x_hat.requires_grad
                sample_time += time.time() - sample_start_time

                train_start_time = time.time()

                log_prob = self.net.log_prob(sample)
                with torch.no_grad():
                    energy = self.ham.energy(sample)
                    loss = log_prob + beta * energy
                assert not energy.requires_grad
                assert not loss.requires_grad
                loss_reinforce = torch.mean((loss - loss.mean()) * log_prob)
                loss_reinforce.backward()

                if self.clip_grad > 0:
                    # nn.utils.clip_grad_norm_(params, self.clip_grad)
                    parameters = list(filter(lambda p: p.grad is not None, params))
                    max_norm = float(self.clip_grad)
                    norm_type = 2
                    total_norm = 0
                    for p in parameters:
                        param_norm = p.grad.data.norm(norm_type)
                        total_norm += param_norm.item() ** norm_type
                        total_norm = total_norm ** (1 / norm_type)
                        clip_coef = max_norm / (total_norm + self.epsilon)
                        for p in parameters:
                            p.grad.data.mul_(clip_coef)

                optimizer.step()

                train_time += time.time() - train_start_time

                if self.print_step and step % self.print_step == 0:
                    free_energy_mean = loss.mean() / beta / bqm.num_variables
                    free_energy_std = loss.std() / beta / bqm.num_variables
                    entropy_mean = -log_prob.mean() / bqm.num_variables
                    energy_mean = energy.mean() / bqm.num_variables
                    mag = sample.mean(dim=0)
                    mag_mean = mag.mean()
                    if step > 0:
                        sample_time /= self.print_step
                        train_time /= self.print_step
                    used_time = time.time() - start_time
                    self.my_log(
                        "beta = {:.3g}, # {}, F = {:.8g}, F_std = {:.8g}, S = {:.5g}, E = {:.5g}, M = {:.5g}, sample_time = {:.3f}, train_time = {:.3f}, used_time = {:.3f}".format(
                            beta,
                            step,
                            free_energy_mean.item(),
                            free_energy_std.item(),
                            entropy_mean.item(),
                            energy_mean.item(),
                            mag_mean.item(),
                            sample_time,
                            train_time,
                            used_time,
                        )
                    )
                    sample_time = 0
                    train_time = 0

            with open(self.fname, "a", newline="\n") as f:
                f.write(
                    "{} {:.3g} {:.8g} {:.8g} {:.8g} {:.8g}\n".format(
                        bqm.num_variables,
                        beta,
                        free_energy_mean.item(),
                        free_energy_std.item(),
                        energy_mean.item(),
                        entropy_mean.item(),
                    )
                )

            beta += self.beta_inc

        return dimod.SampleSet.from_samples(sample.cpu(), energy=energy.cpu(), vartype=bqm.vartype)

    @property
    def properties(self):
        return dict()

    @property
    def parameters(self):
        return {"num_reads": []}


# SK model


class SKModel:
    def __init__(self, n, beta, device, field=0, seed=0):
        self.n = n
        self.beta = beta
        self.field = field
        self.seed = seed
        if seed > 0:
            torch.manual_seed(seed)

        self.J = torch.randn([self.n, self.n]) / math.sqrt(n)
        # Symmetric matrix, zero diagonal
        self.J = torch.triu(self.J, diagonal=1)
        self.J += self.J.t()
        self.J = self.J.to(device)
        self.J.requires_grad = True

        self.C_model = []

        print(
            "SK model with n = {}, beta = {}, field = {}, seed = {}".format(
                n, beta, field, seed
            )
        )

    def exact(self):
        assert self.n <= 20

        Z = 0
        n = self.n
        J = self.J.cpu().to(torch.float64)
        beta = self.beta
        E_min = 0
        n_total = int(math.pow(2, n))

        print("Enumerating...")
        for d in range(n_total):
            s = np.binary_repr(d, width=n)
            b = np.array(list(s)).astype(np.float32)
            b[b < 0.5] = -1
            b = torch.from_numpy(b).view(n, 1).to(torch.float64)
            E = -0.5 * b.t() @ J @ b
            if E < E_min:
                E_min = E
            Z += torch.exp(-beta * E)
            sys.stdout.write("\r{} / {}".format(d, n_total))
            sys.stdout.flush()
        print()

        print("Computing...")
        self.C_model = torch.zeros([n, n]).to(torch.float64)
        for d in range(n_total):
            s = np.binary_repr(d, width=n)
            b = np.array(list(s)).astype(np.float32)
            b[b < 0.5] = -1
            b = torch.from_numpy(b).view(n, 1).to(torch.float64)
            E = -0.5 * b.t() @ J @ b
            prob = torch.exp(-beta * E) / Z
            self.C_model += b @ b.t() * prob
            sys.stdout.write("\r{} / {}".format(d, n_total))
            sys.stdout.flush()
        print()

        # print(self.C_model)
        print(
            "Exact free energy = {:.8f}, paramagnetic free energy = {:.8f}, E_min = {:.8f}".format(
                -torch.log(Z).item() / beta / n, -math.log(2) / beta, E_min.item() / n
            )
        )

    def energy(self, samples):
        """
        Compute energy of samples, samples should be of size [m, n] where n is the number of spins, m is the number of samples.
        """
        samples = samples.view(samples.shape[0], -1)
        assert samples.shape[1] == self.n
        m = samples.shape[0]
        return -0.5 * (
            (samples @ self.J).view(m, 1, self.n) @ samples.view(m, self.n, 1)
        ).squeeze() - self.field * torch.sum(samples, 1)

    def J_diff(self, J):
        """
        Compute difference between true couplings and inferred couplings.
        """
        diff = self.J - J
        diff = diff * diff
        return math.sqrt(torch.mean(diff))

    def save(self):
        self.J = self.J.cpu()
        fsave_name = "n{}b{:.2f}D{}.pickle".format(self.n, self.beta, self.seed)
        with open(fsave_name, "wb") as fsave:
            pickle.dump(self, fsave)
        print("SK model is saved to", fsave_name)


class ResBlock(nn.Module):
    def __init__(self, block):
        super(ResBlock, self).__init__()
        self.block = block

    def forward(self, x):
        return x + self.block(x)


class MaskedLinear(nn.Linear):
    def __init__(self, in_channels, out_channels, n, bias, exclusive):
        super(MaskedLinear, self).__init__(in_channels * n, out_channels * n, bias)
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.n = n
        self.exclusive = exclusive

        self.register_buffer("mask", torch.ones([self.n] * 2))
        if self.exclusive:
            self.mask = 1 - torch.triu(self.mask)
        else:
            self.mask = torch.tril(self.mask)
        self.mask = torch.cat([self.mask] * in_channels, dim=1)
        self.mask = torch.cat([self.mask] * out_channels, dim=0)
        self.weight.data *= self.mask

        # Correction to Xavier initialization
        self.weight.data *= torch.sqrt(self.mask.numel() / self.mask.sum())

    def forward(self, x):
        return nn.functional.linear(x, self.mask * self.weight, self.bias)

    def extra_repr(self):
        return super(
            MaskedLinear, self
        ).extra_repr() + ", exclusive={exclusive}".format(**self.__dict__)


# TODO: reduce unused weights, maybe when torch.sparse is stable
class ChannelLinear(nn.Linear):
    def __init__(self, in_channels, out_channels, n, bias):
        super(ChannelLinear, self).__init__(in_channels * n, out_channels * n, bias)
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.n = n

        self.register_buffer("mask", torch.eye(self.n))
        self.mask = torch.cat([self.mask] * in_channels, dim=1)
        self.mask = torch.cat([self.mask] * out_channels, dim=0)
        self.weight.data *= self.mask

        # Correction to Xavier initialization
        self.weight.data *= torch.sqrt(self.mask.numel() / self.mask.sum())

    def forward(self, x):
        return nn.functional.linear(x, self.mask * self.weight, self.bias)


class MADE(nn.Module):
    def __init__(self, **kwargs):
        super(MADE, self).__init__()
        self.n = kwargs["n"]
        self.net_depth = kwargs["net_depth"]
        self.net_width = kwargs["net_width"]
        self.bias = kwargs["bias"]
        self.z2 = kwargs["z2"]
        self.res_block = kwargs["res_block"]
        self.x_hat_clip = kwargs["x_hat_clip"]
        self.epsilon = kwargs["epsilon"]
        self.device = kwargs["device"]

        self.order = list(range(self.n))
        # self.order = np.random.permutation(self.n)
        # print(self.order)

        # Force the first x_hat to be 0.5
        if self.bias and not self.z2:
            self.register_buffer("x_hat_mask", torch.ones(self.n))
            self.x_hat_mask[0] = 0
            self.register_buffer("x_hat_bias", torch.zeros(self.n))
            self.x_hat_bias[0] = 0.5

        layers = []
        layers.append(
            MaskedLinear(
                1,
                1 if self.net_depth == 1 else self.net_width,
                self.n,
                self.bias,
                exclusive=True,
            )
        )
        for count in range(self.net_depth - 2):
            if self.res_block:
                layers.append(self._build_res_block(self.net_width, self.net_width))
            else:
                layers.append(self._build_simple_block(self.net_width, self.net_width))
        if self.net_depth >= 2:
            layers.append(self._build_simple_block(self.net_width, 1))
        layers.append(nn.Sigmoid())
        self.net = nn.Sequential(*layers)

    def _build_simple_block(self, in_channels, out_channels):
        layers = []
        layers.append(nn.PReLU(in_channels * self.n, init=0.5))
        layers.append(
            MaskedLinear(in_channels, out_channels, self.n, self.bias, exclusive=False)
        )
        block = nn.Sequential(*layers)
        return block

    def _build_res_block(self, in_channels, out_channels):
        layers = []
        layers.append(ChannelLinear(in_channels, out_channels, self.n, self.bias))
        layers.append(nn.PReLU(in_channels * self.n, init=0.5))
        layers.append(
            MaskedLinear(in_channels, out_channels, self.n, self.bias, exclusive=False)
        )
        block = ResBlock(nn.Sequential(*layers))
        return block

    def forward(self, x):
        x = x.view(x.shape[0], -1)
        x_hat = self.net(x)

        if self.x_hat_clip:
            # Clip value and preserve gradient
            with torch.no_grad():
                delta_x_hat = (
                    torch.clamp(x_hat, self.x_hat_clip, 1 - self.x_hat_clip) - x_hat
                )
            assert not delta_x_hat.requires_grad
            x_hat = x_hat + delta_x_hat

        # Force the first x_hat to be 0.5
        if self.bias and not self.z2:
            x_hat = x_hat * self.x_hat_mask + self.x_hat_bias

        return x_hat

    # sample = +/-1, +1 = up = white, -1 = down = black
    # sample.dtype == default_dtype_torch
    # x_hat = p(x_{i, j} == +1 | x_{0, 0}, ..., x_{i, j - 1})
    # 0 < x_hat < 1
    # x_hat will not be flipped by z2
    def sample(self, batch_size):
        sample = torch.zeros(
            [batch_size, self.n], dtype=default_dtype_torch, device=self.device
        )
        for i in range(self.n):
            x_hat = self.forward(sample)
            sample[:, i] = torch.bernoulli(x_hat[:, i]).to(default_dtype_torch) * 2 - 1

        if self.z2:
            # Binary random int 0/1
            flip = (
                torch.randint(
                    2, [batch_size, 1], dtype=sample.dtype, device=sample.device
                )
                * 2
                - 1
            )
            sample *= flip

        sample = sample[:, self.order]
        x_hat = x_hat[:, self.order]

        return sample, x_hat

    def _log_prob(self, sample, x_hat):
        mask = (sample + 1) / 2
        log_prob = torch.log(x_hat + self.epsilon) * mask + torch.log(
            1 - x_hat + self.epsilon
        ) * (1 - mask)
        log_prob = log_prob.view(log_prob.shape[0], -1).sum(dim=1)
        return log_prob

    def log_prob(self, sample):
        sample[:, self.order] = sample
        sample = sample.view(sample.shape[0], -1)

        x_hat = self.forward(sample)
        log_prob = self._log_prob(sample, x_hat)

        if self.z2:
            # Density estimation on inverted sample
            sample_inv = -sample
            x_hat_inv = self.forward(sample_inv)
            log_prob_inv = self._log_prob(sample_inv, x_hat_inv)
            log_prob = torch.logsumexp(torch.stack([log_prob, log_prob_inv]), dim=0)
            log_prob = log_prob - log(2)

        return log_prob


class ModifiedSKModel(SKModel):
    def __init__(self, n, device, bqm, field=0, seed=0):
        self.n = n
        self.field = field
        self.seed = seed
        if seed > 0:
            torch.manual_seed(seed)
        J = self._bqm_to_couplings(bqm)
        self.J = torch.tensor(J, dtype=torch.float32)
        # Symmetric matrix, zero diagonal
        self.J = self.J.to(device)
        self.J.requires_grad = True
        self.C_model = []

    def _bqm_to_couplings(self, bqm):
        J = np.zeros((bqm.num_variables, bqm.num_variables))
        h, JJ, offset = bqm.to_ising()
        for (i, v) in h.items():
            J[i, i] = v
        for ((i, j), v) in JJ.items():
            J[i, j] = v
        return J
