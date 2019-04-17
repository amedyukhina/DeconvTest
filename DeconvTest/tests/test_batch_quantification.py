import unittest

from ddt import ddt
import os
import pandas as pd
import shutil

from DeconvTest.batch import simulation as sim
from DeconvTest.batch import quantification as quant


@ddt
class TestSimulation(unittest.TestCase):

    def test_simulate(self):
        sim.generate_cell_parameters('data/params.csv', number_of_cells=2)
        sim.generate_cells_batch(params_file='data/params.csv',
                                 outputfolder='data/cells/',
                                 resolution=1,
                                 print_progress=False)
        sim.generate_psfs_batch('data/psfs',
                                sigmas=[1.5],
                                aspect_ratios=[4],
                                resolution=1,
                                print_progress=False)
        sim.convolve_batch('data/cells/',
                           'data/psfs',
                           'data/convolved/',
                           print_progress=False)

        quant.segment_batch(inputfolder='data/convolved',
                            outputfolder='data/segmented',
                            thr=5,
                            preprocess=True,
                            print_progress=False,
                            log_computing_time=True)

        files = os.listdir('data/segmented')
        self.assertEqual(len(files), 1)
        files = os.listdir('data/segmented/psf_sigma_1.5_aspect_ratio_4')
        self.assertEqual(len(files), 4)
        self.assertEqual(os.path.exists('data/log/psf_sigma_1.5_aspect_ratio_4_cell_000.csv'), True)

        quant.compute_binary_accuracy_measures_batch(inputfolder='data/convolved',
                                                     reffolder='data/cells',
                                                     outputfolder='data/binary_accuracy',
                                                     print_progress=False)
        files = os.listdir('data/binary_accuracy')
        self.assertEqual(len(files), 1)
        files = os.listdir('data/binary_accuracy/psf_sigma_1.5_aspect_ratio_4')
        self.assertEqual(len(files), 2)
        self.assertEqual(os.path.exists('data/binary_accuracy.csv'), True)

        quant.combine_log('data/log')
        self.assertEqual(os.path.exists('data/log.csv'), True)

        quant.extract_metadata('data/binary_accuracy.csv', 0.5)
        stat = pd.read_csv('data/binary_accuracy.csv', sep='\t', index_col=0)
        for col in ['Kind', 'Voxel size y', 'resolution']:
            self.assertIn(col, stat.columns)

        quant.extract_metadata('data/log.csv', 0.5)
        stat = pd.read_csv('data/log.csv', sep='\t', index_col=0)
        for col in ['Kind', 'Voxel size x', 'resolution']:
            self.assertIn(col, stat.columns)

        shutil.rmtree('data/')


if __name__ == '__main__':
    unittest.main()



