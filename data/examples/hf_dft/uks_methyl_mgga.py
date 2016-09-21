#!/usr/bin/env python
#JSON {"lot": "UKS/6-31G*",
#JSON  "scf": "CDIISSCFSolver",
#JSON  "linalg": "CholeskyLinalgFactory",
#JSON  "difficulty": 6,
#JSON  "description": "Basic UKS DFT example with MGGA exhange-correlation functional (TPSS)"}

from horton import *  # pylint: disable=wildcard-import,unused-wildcard-import


# Load the coordinates from file.
# Use the XYZ file from HORTON's test data directory.
fn_xyz = context.get_fn('test/methyl.xyz')
mol = IOData.from_file(fn_xyz)

# Create a Gaussian basis set
obasis = get_gobasis(mol.coordinates, mol.numbers, '6-31g*')

# Create a linalg factory
lf = DenseLinalgFactory(obasis.nbasis)

# Compute Gaussian integrals
olp = obasis.compute_overlap(lf)
kin = obasis.compute_kinetic(lf)
na = obasis.compute_nuclear_attraction(mol.coordinates, mol.pseudo_numbers, lf)
er = obasis.compute_electron_repulsion(lf)

# Define a numerical integration grid needed the XC functionals
grid = BeckeMolGrid(mol.coordinates, mol.numbers, mol.pseudo_numbers)

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
    UGridGroup(obasis, grid, [
        ULibXCMGGA('x_tpss'),
        ULibXCMGGA('c_tpss'),
    ]),
    UTwoIndexTerm(na, 'ne'),
]
ham = UEffHam(terms, external)

# Decide how to occupy the orbitals (5 alpha electrons, 4 beta electrons)
occ_model = AufbauOccModel(5, 4)

# Converge WFN with CDIIS SCF
# - Construct the initial density matrix (needed for CDIIS).
occ_model.assign(exp_alpha, exp_beta)
dm_alpha = exp_alpha.to_dm()
dm_beta = exp_beta.to_dm()
# - SCF solver
scf_solver = CDIISSCFSolver(1e-6)
scf_solver(ham, lf, olp, occ_model, dm_alpha, dm_beta)

# Derive orbitals (coeffs, energies and occupations) from the Fock and density
# matrices. The energy is also computed to store it in the output file below.
fock_alpha = lf.create_two_index()
fock_beta = lf.create_two_index()
ham.reset(dm_alpha, dm_beta)
ham.compute_energy()
ham.compute_fock(fock_alpha, fock_beta)
exp_alpha.from_fock_and_dm(fock_alpha, dm_alpha, olp)
exp_beta.from_fock_and_dm(fock_beta, dm_beta, olp)

# Assign results to the molecule object and write it to a file, e.g. for
# later analysis. Note that the CDIIS algorithm can only really construct an
# optimized density matrix and no orbitals.
mol.title = 'UKS computation on methyl'
mol.energy = ham.cache['energy']
mol.obasis = obasis
mol.exp_alpha = exp_alpha
mol.exp_beta = exp_beta
mol.dm_alpha = dm_alpha
mol.dm_beta = dm_beta

# useful for post-processing (results stored in double precision):
mol.to_file('methyl.h5')

# CODE BELOW IS FOR horton-regression-test.py ONLY. IT IS NOT PART OF THE EXAMPLE.
rt_results = {
    'energy': ham.cache['energy'],
    'exp_alpha': exp_alpha.energies,
    'exp_beta': exp_beta.energies,
    'nn': ham.cache["energy_nn"],
    'kin': ham.cache["energy_kin"],
    'ne': ham.cache["energy_ne"],
    'grid': ham.cache["energy_grid_group"],
    'hartree': ham.cache["energy_hartree"],
}
# BEGIN AUTOGENERATED CODE. DO NOT CHANGE MANUALLY.
import numpy as np  # pylint: disable=wrong-import-position
rt_previous = {
    'nn': 9.0797849426636361,
    'energy': -39.8366773479259,
    'ne': -109.92841125860787,
    'grid': -6.447610544950923,
    'exp_alpha': np.array([
        -10.019635076738151, -0.61357555665159147, -0.36281213390879258,
        -0.36276528782853157, -0.19070293326772153, 0.071676580515679836,
        0.14516276093823552, 0.14520445336541019, 0.51037249458810763,
        0.55245497246844311, 0.55247011455993456, 0.66897270052023006,
        0.84604700858519855, 0.84613026545140646, 0.8985815855427518, 1.6194517568114521,
        1.6194677518472709, 1.9300340527577871, 2.0952910889031018, 2.0961171453114136
    ]),
    'hartree': 28.092381575581598,
    'exp_beta': np.array([
        -10.004003922798798, -0.5755426452796244, -0.35601452017897395,
        -0.35588391063394487, -0.065485342591881074, 0.098337149121918571,
        0.15959808034823597, 0.1598608740478755, 0.5691762050289414, 0.56946718254783601,
        0.60089298391388568, 0.70441988947800827, 0.87990225342683714,
        0.88198311255363426, 0.95807927778740076, 1.7277678928512425, 1.7299240596423355,
        2.0576938854035935, 2.1741132806022021, 2.1750154723644286
    ]),
    'kin': 39.36717793738765,
}
