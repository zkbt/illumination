from playground.process_sparse import *

orbit = 'orbit-8196'
directories_pattern = '/scratch2/zkbt/orbit-8196/stamps/cam1/cam1_spm1_*'
stamps_directory = '/scratch2/zkbt/orbit-8196/stamps/'
combine_times_to_stamps(directories_pattern=directories_pattern, stamps_directory=stamps_directory)
