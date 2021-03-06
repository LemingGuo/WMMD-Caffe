# coding: utf-8
#fine tune num_of_kernel
import os
from google.protobuf import text_format
caffe_root = '../'
import sys
sys.path.insert(0,caffe_root + 'python')
import caffe
import default
from caffe.proto import caffe_pb2 as pb
#this part need to modify according to your path
pwd = os.getcwd()
model_path = default.model_path
solver_config_path = default.solver_config_path
net_config_path = default.net_config_path
Solver_TUNE = False
Net_TUNE = True
Nreapt = default.Nreapt
#fistly you need to set the solver and net parameter for default
#solver_default = {
#    'test_iter':14,
#    'test_interval': 200,
#    'base_lr':0.001,
#    'max_iter':10000,
#    'momentum':0.9,
#    'stepsize':500,
#    'snapshot':10000,
#    'snapshot_prefix':model_path[1:]+"mmd",
#    'net':net_config_path[1:],
#}
solver_default = default.solver

mmd_default = default.mmd
#{
#    #work in alex net
#    "mmd_fc7":1.0,
#    "mmd_fc8":0.1,
#    #work in googlenet
#    "mmd_loss3":0.3,
#    "mmd_4d":2,
#    "mmd_4e":3,
#}

iter_of_epoch = default.iter_of_epoch
num_class_default = default.num_class
mmd_lock_default = default.mmd_lock
entropy_weight_default = default.entropy_weight
#{
#    "entropy_loss":0.4,
#}
entropy_thresh_default = default.entropy_thresh

kernel_default = default.kernel
#pwd = os.getcwd()
#model_path = "../models/amazon_to_caltech/"
#solver_config_path = model_path + "solver.prototxt"
#net_config_path = model_path + "adaptive_train_val.prototxt"
#
##Fistly you need to set the solver and net parameter for default
#Solver_TUNE = False
#Net_TUNE = True
#Nreapt = 2
#solver_default = {
#    'test_iter':14,
#    'test_interval': 200,
#    'base_lr':0.00316,
#    'max_iter':10000,
#    'momentum':0.9,
#    'stepsize':500,
#    'snapshot':10000,
#    'snapshot_prefix':model_path[1:]+"mmd",
#    'net':net_config_path[1:],
#}
#
#mmd_default = {
#    "mmd_fc7":0.3,
#    "mmd_fc8":0.01,
#    "mmd_loss3":0.3,
#    "mmd_4d":2,
#    "mmd_4e":3,
#}
#
#iter_of_epoch = 32
#num_class_default = 10
#mmd_lock_default = 1
#entropy_weight_default = {
#    "entropy_loss":0.4,
#}
#
#entropy_thresh_default = 10.0
#
#kernel_default = 5

#do not change the rest
if(not os.path.exists(solver_config_path)):
    #define solver.prototxt
    print solver_config_path + " not exist"
else:
    ########## solver
    print "sovler define"
    s = pb.SolverParameter()

    #read and parse solver prototxt
    #read_solver_file = open(solver_config_path,'rb')
    solver_str = str(open(solver_config_path,'rb').read())
    text_format.Parse(solver_str,s)

    #set parameter
    s.test_iter[0] = solver_default['test_iter']
    s.max_iter = solver_default['max_iter']


if(not os.path.exists(net_config_path)):
    print net_config_path  +" not exist"
else:
    ############## net
    net = pb.NetParameter()

    #read and parse net file
    #read_net_file = open(net_config_path,'rb')
    net_str = str(open(net_config_path,'rb').read())
    text_format.Parse(net_str,net);

#lr_list = [10**(-i*0.5) for i in range(5,11)]
kernel_num_list = [1,3,5,7,10]
for kernel_num in kernel_num_list:
    print kernel_num

    #set default values for solver
    for key in solver_default:
        set_command = "s."+str(key.format())+'=' + "solver_default[\"" + str(key.format())+"\"]"
        if (key=="test_iter"):
            set_command = "s."+str(key.format())+'[0]=' + "solver_default[\"" + str(key.format())+"\"]"
        exec(set_command)

    #fine tune solver in this part
    if Solver_TUNE:
        s.base_lr = lr

    #write to solver file
    output = text_format.MessageToString(s)
    out_file = open(solver_config_path,'w')
    out_file.write(output)
    out_file.close()


    #set default values for net
    for layer in net.layer:
        name = layer.name
        if name in mmd_default:
            mmd_lambda = mmd_default[name]
            layer.mmd_param.mmd_lambda = mmd_lambda
            layer.mmd_param.num_of_kernel = kernel_default
            layer.mmd_param.entropy_thresh = entropy_thresh_default
            layer.mmd_param.iter_of_epoch = iter_of_epoch
            layer.mmd_param.num_class = num_class_default
            layer.mmd_param.mmd_lock = mmd_lock_default

        if name in entropy_weight_default:
            loss_weight = entropy_weight_default[name]
            layer.loss_weight = loss_weight

   #fine tune net in this part
    if Net_TUNE:
        #fine tune kernel number
        kernel_num_tmp = {
            'mmd_fc7':kernel_num,
            'mmd_fc8':kernel_num,
        }

        for layer in net.layer:
            name  = layer.name
            if name in kernel_num_tmp:
                layer.mmd_param.num_of_kernel = kernel_num

    #write to net file
    output = text_format.MessageToString(net)
    out_file = open(net_config_path,'w')
    out_file.write(output)
    out_file.close()

    #solve
    os.chdir(caffe_root)
    #command_ = 'bash ' + model_path[1:] + 'alex_net_train.sh'
    command_ = 'bash ' + default.script
    for iparrel in range(Nreapt):
        os.system(command_)
    os.chdir(pwd)

#read_solver_file.close()
#read_net_file.close()
#caffe.set_device(0)
#caffe.set_mode_gpu()
#solver = None
#solver = caffe.get_solver(solver_config_path)
#print s.max_iter
#for it in range(s.max_iter):
#    solver.step(1)




