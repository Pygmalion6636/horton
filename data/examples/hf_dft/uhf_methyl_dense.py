#!/usr/bin/env python
#JSON {"lot": "UHF/3-21G",
#JSON  "scf": "PlainSCFSolver",
#JSON  "linalg": "DenseLinalgFactory",
#JSON  "difficulty": 1,
#JSON  "description": "Basic UHF example with dense matrices"}

from horton import *  # pylint: disable=wildcard-import,unused-wildcard-import


# Load the coordinates from file.
# Use the XYZ file from HORTON's test data directory.
fn_xyz = context.get_fn('test/methyl.xyz')
mol = IOData.from_file(fn_xyz)

# Create a Gaussian basis set
obasis = get_gobasis(mol.coordinates, mol.numbers, '3-21G')

# Create a linalg factory
lf = DenseLinalgFactory(obasis.nbasis)

# Compute Gaussian integrals
olp = obasis.compute_overlap(lf)
kin = obasis.compute_kinetic(lf)
na = obasis.compute_nuclear_attraction(mol.coordinates, mol.pseudo_numbers, lf)
er = obasis.compute_electron_repulsion(lf)

# Create alpha orbitals
exp_alpha = lf.create_expansion()
exp_beta = lf.create_expansion()

# Initial guess
guess_core_hamiltonian(olp, kin, na, exp_alpha, exp_beta)

# Construct the restricted HF effective Hamiltonian
external = {'nn': compute_nucnuc(mol.coordinates, mol.pseudo_numbers)}
terms = [
    UTwoIndexTerm(kin, 'kin'),
    UDirectTerm(er, 'hartree'),
    UExchangeTerm(er, 'x_hf'),
    UTwoIndexTerm(na, 'ne'),
]
ham = UEffHam(terms, external)

# Decide how to occupy the orbitals (5 alpha electrons, 4 beta electrons)
occ_model = AufbauOccModel(5, 4)

# Converge WFN with plain SCF
scf_solver = PlainSCFSolver(1e-6)
scf_solver(ham, lf, olp, occ_model, exp_alpha, exp_beta)

# Assign results to the molecule object and write it to a file, e.g. for
# later analysis
mol.title = 'UHF computation on methyl'
mol.energy = ham.cache['energy']
mol.obasis = obasis
mol.exp_alpha = exp_alpha
mol.exp_beta = exp_beta

# useful for visualization:
mol.to_file('methyl.molden')
# useful for post-processing (results stored in double precision)
mol.to_file('methyl.h5')


# CODE BELOW IS FOR horton-regression-test.py ONLY. IT IS NOT PART OF THE EXAMPLE.
rt_results = {
    'energy': ham.cache['energy'],
    'exp_alpha': exp_alpha.energies,
    'exp_beta': exp_beta.energies,
    'nn': ham.cache["energy_nn"],
    'kin': ham.cache["energy_kin"],
    'ne': ham.cache["energy_ne"],
    'ex': ham.cache["energy_x_hf"],
    'hartree': ham.cache["energy_hartree"],
}
# BEGIN AUTOGENERATED CODE. DO NOT CHANGE MANUALLY.
import numpy as np  # pylint: disable=wrong-import-position
rt_previous = {
    'nn': 9.0797849426636361,
    'energy': -39.331221904962476,
    'ne': -109.07151185985309,
    'kin': 38.93357262027517,
    'exp_alpha': np.array([
        -11.194977911345209, -0.92420112228139029, -0.55513937861886897,
        -0.55513936656338159, -0.38934656780805477, 0.25358440732842569,
        0.3356648031115444, 0.33566482061595093, 0.93322912329048002, 0.98518834644332498,
        0.98518849306172662, 1.1024490804164022, 1.3032622584429243, 1.3032623363395086,
        1.6761192066890565
    ]),
    'hartree': 27.840836401008197,
    'exp_beta': np.array([
        -11.16903157149193, -0.8181773727532734, -0.53903034297663543,
        -0.53903033685266155, 0.16303091192059177, 0.28378927314963531,
        0.34897199801702677, 0.34897201610275924, 1.0010276475405742, 1.0010277998402903,
        1.0836169709197505, 1.1060903534350084, 1.3066657923992511, 1.3066658801221409,
        1.7272407098243421
    ]),
    'ex': -6.113904009056382,
}
