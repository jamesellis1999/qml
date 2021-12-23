r"""

Qubit tapering
==============

.. meta::
    :property="og:description": Learn how to taper off qubits
    :property="og:image": https://pennylane.ai/qml/_images/ qubit_tapering.png

.. related::
    tutorial_quantum_chemistry Quantum chemistry with PennyLane
    tutorial_vqe A brief overview of VQE
    tutorial_givens_rotations Givens rotations for quantum chemistry
    tutorial_adaptive_circuits Adaptive circuits for quantum chemistry


*Author: PennyLane dev team. Posted:  2021. Last updated: XX January 2022*

The performance of variational quantum algorithms is considerably limited by the number of qubits
required to represent the trial wavefunction space. In the context of quantum chemistry, this
limitation hinders the treatment of large molecules with algorithms such as the variational quantum
eigensolver (VQE). Several approaches have been developed to reduce the qubit requirements for
fixed-accuracy electronic structure calculations. In this tutorial, we demonstrate the
symmetry-based qubit tapering method which allows reducing the number of qubits required to perform
molecular quantum simulations by leveraging the symmetries that are present in molecular
Hamiltonians [#bravyi2017]_ [#setia2019]_. Let's have a look at the theory first.

Qubit tapering with symmetries
------------------------------

The key step in this method is to find a unitary operator, from the symmetries present in a
Hamiltonian, and use this operator to transform the Hamiltonian in such a way that it acts
trivially, with an identity operator or at most one Pauli operator, on a set of :math:`k` qubits.
This guarantees that each of these pauli operators commutes with the Hamiltonian and can be replaced
with one of its eigenvalues.

The molecular qubit Hamiltonian is constructed as a linear combination of Pauli strings as

      .. math:: H = \sum_{i=1}^r c_i \eta_i

where :math:`c_i` is a real coefficient and :math:`\eta_i` is a Pauli string acting on a number of
qubits. The Hamiltonian :math:`H` is constructed such that :math:`\eta_i \in P_M` where

      .. math:: P_M = \pm \left \{ I, \sigma_x, \sigma_y, \sigma_z  \right \}^{\bigotimes M},

and :math:`M` is the total number of qubits. The aim here is to find a unitary operator :math:`U`
that is applied to :math:`H` to provide a transformed Hamiltonian :math:`H'`

      .. math:: H' = U^{\dagger} H U = \sum_{i=1}^r c_i \mu_i,

such that each :math:`\mu_i` term acts trivially on a set of :math:`k` qubits and
:math:`\mu_i \equiv U^{\dagger} \eta_i U`.

Recalling that a Clifford group :math:`C` is defined as a set of unitary operators :math:`U` such
that :math:`U \eta U^{\dagger} \in P_M` for :math:`\eta \in P_M`, we can conclude that
:math:`\mu \in P_M`.

We now define the Abelian group :math:`S \in P_M` such that each term in :math:`S` commutes with
:math:`\eta`. It has been shown `here <https://arxiv.org/abs/1701.08213>`__ that for any Abelian
group :math:`S \in P_M` and :math:`-I \notin S`, there is a set set of generators
:math:`S = \left \langle \tau_1, ..., \tau_k \right \rangle` such that

      .. math:: \tau_i = U \sigma_x^i U^{\dagger}.

Based on the definition of :math:`S`, we already know that :math:`[\tau_i ,\eta_j] = 0`,
then it is easy to show that :math:`[\mu_j, \sigma_x^i] = 0`. This implies that there are :math:`k`
terms in :math:`\mu_j` that are either :math:`I` or :math:`\sigma_x` which can then be replaced with
their eigenvalues :math:`\pm 1` and tapered off from :math:`H'`.

"""

import pennylane as qml
from pennylane import numpy as np

symbols = ["H", "H"]
geometry = np.array([[-0.672943567415407, 0.0, 0.0],
                     [ 0.672943567415407, 0.0, 0.0]], requires_grad=True)

##############################################################################
# We now create a molecule object that stores all the molecular parameters needed to construct the
# molecular electronic Hamiltonian.

mol = qml.hf.Molecule(symbols, geometry)
hamiltonian = qml.hf.generate_hamiltonian(mol)(geometry)
print(hamiltonian)

##############################################################################
# The Hamiltonian contains 15 terms acting on one to four qubits. This Hamiltonian can be
# transformed such that it acts trivially on some of the qubits.

generators, paulix_ops = qml.hf.generate_symmetries(hamiltonian, len(hamiltonian.wires))

paulix_sector = [1, -1, -1]

H_tapered = qml.hf.transform_hamiltonian(hamiltonian, generators, paulix_ops, paulix_sector)

print(H_tapered)

##############################################################################
# Conclusions
# -----------
#
#
# References
# ----------
#
# .. [#bravyi2017]
#
#     Sergey Bravyi, Jay M. Gambetta, Antonio Mezzacapo, Kristan Temme, "Tapering off qubits to
#     simulate fermionic Hamiltonians". `arXiv:1701.08213
#     <https://arxiv.org/abs/1701.08213>`__
#
# .. [#setia2019]
#
#     Kanav Setia, Richard Chen, Julia E. Rice, Antonio Mezzacapo, Marco Pistoia, James Whitfield,
#     "Reducing qubit requirements for quantum simulation using molecular point group symmetries".
#     `arXiv:1910.14644 <https://arxiv.org/abs/1910.14644>`__
