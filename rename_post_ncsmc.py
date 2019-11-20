"""renames files created by ncsmc"""
import os
import argparse

# IF YOU'RE RUNNING THIS WITH A BATCH SCRIPT, YOU DON'T HAVE TO EDIT ANYTHING!
# parameters describing nucleus, potential, ...
projectile = 'n'
target = 'Li8'
potential = 'n3lo-NN3Nlnl-srg2.0'
freq = '20'
Nmax = '6'
affix = ''


def rename_all(projectile=projectile, target=target, potential=potential,
               freq=freq, Nmax=Nmax, affix=affix):
    """
    given a bunch of nucleus details, rename files after running ncsmc

    Example parameters:
    projectile = 'n'
    target = 'Li8'
    potential = 'n3lo-NN3Nlnl-srg2.0'
    freq = '20'
    Nmax = '4'
    affix = ''
    """

    # stuff to be written into your filenames e.g. x.y --> x_details.y
    details = projectile+target+'_'+potential+'_'+freq+'_Nmax'+Nmax
    if len(affix) > 0:
        details = details+'_'+affix

    def rename(prefix, suffix=''):
        """
        Renames a file whose name consists of a prefix and suffix

        e.g. phase_shift.agr --> phase_shift_nLi8_n3lo-srg2.0_20_Nmax11.agr

        (prefix = "phase_shift", suffix = ".agr", but suffix !always= extension)

        The stuff that gets added in the middle is defined as 'details' above.
        """
        old_file = prefix + suffix
        # if old_file exists and is in fact a file
        if os.path.isfile(old_file):
            # and if old_file contains more than just \n or something
            if os.path.getsize(old_file) > 2:
                # rename to new_file by adding details in the middle
                new_file = prefix + '_' + details + suffix
                os.rename(old_file, new_file)
                print("renamed "+old_file)

    # rename all the following files, if they exist
    rename('t', '.o')
    rename('kernels_n_np', '.dat')
    rename('kernels_plot_n_np', '.dat')
    rename('RGM_kernels_n_np', '.dat')
    rename('model_space_wf', '.agr')
    rename('model_space_wf_RGM', '.agr')
    rename('model_space_wf_NCSMC', '.agr')
    rename('wavefunction', '.agr')
    rename('wavefunction_NCSMC', '.agr')
    rename('wavefunction_xy', '.agr')
    rename('norm_sqrt_r_rp', '.dat')
    rename('norm_sqrt_r_rp_RGM', '.dat')
    rename('scattering_wf', '.agr')
    rename('scattering_wf_NCSMC', '.agr')
    rename('ortogkernel_r_rp', '.dat')
    rename('phase_shift', '.agr')
    rename('eigenphase_shift', '.agr')
    rename('ncsm_rgm_Am3_3.out')
    rename('ncsm_rgm_Am2_2.out')
    rename('ncsm_rgm_Am2_1_1.out')
    rename('NCSMC_form_factors_g_h', '.dat')
    rename('expansion_coeff_NCSMC', '.dat')
    rename('file_S_matrix', '.tmp_fmt')
    rename('InputForRmatrixAnalysis', '.tmp')
    rename('Rmatrix', '.tmp')
    rename('sigma_tot', '.agr')
    rename('sigma_reac', '.agr')
    rename('dsigma_dOmega', '.agr')
    rename('iT11', '.agr')
    rename('T0022_target-beam', '.agr')


if __name__ == "__main__":
    # get command line arguments if possible, otherwise use defaults up top
    parser = argparse.ArgumentParser("Rename Files After NCSMC")
    parser.add_argument("--projectile", nargs='?', const=projectile,
                        help="projectile", type=str)
    parser.add_argument("--target", nargs='?', const=target,
                        help="target", type=str)
    parser.add_argument("--potential", nargs='?', const=potential,
                        help="potential", type=str)
    parser.add_argument("--freq", nargs='?', const=freq,
                        help="frequency", type=str)
    parser.add_argument("--Nmax", nargs='?', const=Nmax, help="Nmax", type=str)
    parser.add_argument("--affix", nargs='?', const=affix,
                        help="extra text to affix to filenames", type=str)

    # get args in dict form
    args = vars(parser.parse_args())

    # then run the renaming function with those variables
    rename_all(**args)
    print("done renaming!")