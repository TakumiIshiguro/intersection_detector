#!/usr/bin/env python3

import roslib
roslib.load_manifest('intersection_detector')
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
# from intersection_detect_mobilenetv2 import *
# from intersection_detect_LRCN import *
# from intersection_detect_LRCN_no_buffer import *
# from intersection_detect_LRCN_all import *
from bag2torch_lstm import *
from skimage.transform import resize
from geometry_msgs.msg import Twist
from geometry_msgs.msg import PoseArray
from std_msgs.msg import Int8,String
from std_srvs.srv import Trigger
from std_msgs.msg import Int8MultiArray
# from waypoint_nav.msg import cmd_dir_intersection
from scenario_navigation_msgs.msg import cmd_dir_intersection
# from geometry_msgs.msg import PoseWithCovarianceStamped
from std_srvs.srv import Empty
from std_srvs.srv import SetBool, SetBoolResponse
import os
import time
import sys
import tf
from nav_msgs.msg import Odometry

class intersection_detector_node:
    def __init__(self):
        rospy.init_node('intersection_detector_node', anonymous=True)
        self.class_num = 8
        self.b2t = bag_to_tensor()
        self.bridge = CvBridge()
        # self.intersection_pub = rospy.Publisher("passage_type",String,queue_size=1)
        self.intersection_pub = rospy.Publisher("passage_type",cmd_dir_intersection,queue_size=1)
        # self.image_sub = rospy.Subscriber("/camera_center/image_raw", Image, self.callback)
        # self.image_sub = rospy.Subscriber("/image_center", Image, self.callback)
        # self.image_sub = rospy.Subscriber("/image_left", Image, self.callback)
        self.image_sub = rospy.Subscriber("/image_right", Image, self.callback)
        # self.image_left_sub = rospy.Subscriber("/camera_left/rgb/image_raw", Image, self.callback_left_camera)
        # self.image_right_sub = rospy.Subscriber("/camera_right/rgb/image_raw", Image, self.callback_right_camera)
        self.srv = rospy.Service('/training_intersection', SetBool, self.callback_dl_training)
        self.loop_srv = rospy.Service('/loop_count', SetBool, self.callback_dl_training)
        
        # self.mode_save_srv = rospy.Service('/model_save_intersection', Trigger, self.callback_model_save)
        self.cmd_dir_sub = rospy.Subscriber("/cmd_dir_intersection", cmd_dir_intersection, self.callback_cmd,queue_size=1)
        self.min_distance = 0.0
        self.action = 0.0
        self.episode = 0
        # self.intersection =String()
        self.intersection = cmd_dir_intersection()
        self.path_pose = PoseArray()
        self.cv_image = np.zeros((480,640,3), np.uint8)
        self.cv_left_image = np.zeros((480,640,3), np.uint8)
        self.cv_right_image = np.zeros((480,640,3), np.uint8)
        self.learning = True
        self.learning_tensor_flag = True
        self.select_dl = False
        self.start_time = time.strftime("%Y%m%d_%H:%M:%S")
        # self.path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/result'
        
        # self.load_image_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/image/image_center/image.pt'
        # self.load_label_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/label/center_label/label.pt'

        # self.load_image_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/image/image_left/image.pt'
        # self.load_label_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/label/left_label/label.pt'
        
        # self.load_image_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/image/image_right/image.pt'
        # self.load_label_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/label/right_label/label.pt'

        # self.load_center_image_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/image/image_center/image.pt'
        # self.load_center_label_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/label/center_label/label.pt'

        # self.load_left_image_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/image/image_left/image.pt'
        # self.load_left_label_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/label/left_label/label.pt'
        
        # self.load_right_image_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/image/image_right/image.pt'
        # self.load_right_label_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/label/right_label/label.pt'
        
        # self.load_center_image_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/image/image_center_blind/image.pt'
        # self.load_center_label_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/label/center_label_blind/label.pt'

        # self.load_left_image_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/image/image_left_blind/image.pt'
        # self.load_left_label_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/label/left_label_blind/label.pt'
        
        # self.load_right_image_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/image/image_right_blind/image.pt'
        # self.load_right_label_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/label/right_label_blind/label.pt'

        self.load_image_path_1 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/image/f2/image.pt'
        self.load_label_path_1 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/label/f2/label.pt'
        
        self.load_image_path_2 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/image/g/image.pt'
        self.load_label_path_2 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/label/g/label.pt'
        
        self.load_image_path_3 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/image/h/image.pt'
        self.load_label_path_3 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/label/h/label.pt'

        self.load_image_path_4 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/image/i/image.pt'
        self.load_label_path_4 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/label/i/label.pt'

        self.load_image_path_5 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/image/j/image.pt'
        self.load_label_path_5 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/label/j/label.pt'
        
        self.load_image_path_6 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/image/k/image.pt'
        self.load_label_path_6 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/label/k/label.pt'
        
        self.load_image_path_7 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/image/l/image.pt'
        self.load_label_path_7 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/label/l/label.pt'

        self.load_image_path_8 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/image/m/image.pt'
        self.load_label_path_8 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/label/m/label.pt'

        self.load_image_path_9 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/image/n/image.pt'
        self.load_label_path_9 = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/label/n/label.pt'
        
        # self.load_add_image_path = '/home/rdclab/orne_ws/src/intersection_detector/data/dataset/lrcn/image//image.pt'
        # self.load_add_label_path = '/home/rdclab/orne_ws/src/intersection_detector/data/dataset/lrcn/label//label.pt'

        # self.load_image_path = '/home/rdclab/orne_ws/src/intersection_detector/data/dataset/lrcn/image/add/re_cat/blind_add_area/image.pt'
        # self.load_label_path = '/home/rdclab/orne_ws/src/intersection_detector/data/dataset/lrcn/label/add/re_cat/blind_add_area/label.pt'
        
        # self.load_image_path = '/home/rdclab/orne_ws/src/intersection_detector/data/dataset/lrcn/image/_add_ele_go/image.pt'
        # self.load_label_path = '/home/rdclab/orne_ws/src/intersection_detector/data/dataset/lrcn/label/_add_ele_go/label.pt'
        # self.load_image_path = '/home/rdclab/orne_ws/src/intersection_detector/data/dataset/lrcn/image/add/re_cat/blind_add_ele_go/image.pt'
        # self.load_label_path = '/home/rdclab/orne_ws/src/intersection_detector/data/dataset/lrcn/label/add/re_cat/blind_add_ele_go/label.pt'
        # self.load_image_path = '/home/rdclab/orne_ws/src/intersection_detector/data/dataset/lrcn/image/add/re_cat/ele_dai_oku+dai_oku_migi/image.pt'
        # self.load_label_path = '/home/rdclab/orne_ws/src/intersection_detector/data/dataset/lrcn/label/add/re_cat/ele_dai_oku+dai_temae_migi/label.pt'

        # self.load_image_path = '/home/rdclab/Data/tensor/intersection_detactor/dataset/lrcn/image/re_cat/right_add_area_re_ele_dai_temae_go/image.pt'
        # self.load_label_path = '/home/rdclab/Data/tensor/intersection_detactor/dataset/lrcn/label/re_cat/right_add_area_re_ele_dai_temae_go/label.pt'
        # self.load_image_path = '/home/rdclab/Data/tensor/intersection_detactor/dataset/lrcn/image/re_cat/right_add_area_re_ele_dai_temae_go/image.pt'
        # self.load_label_path = '/home/rdclab/Data/tensor/intersection_detactor/dataset/lrcn/label/re_cat/right_add_area_re_ele_dai_temae_go/label.pt'

        # self.load_path =roslib.packages.get_pkg_dir('intersection_detector') + '/data/model/lrcn/real/frame16/hz8/30ep/0707_bright_dark_all/model_gpu.pt'
        # self.load_path =roslib.packages.get_pkg_dir('intersection_detector') + '/data/model/lrcn/real/frame16/hz8/30ep/0904_right_blind_add/model_gpu.pt'
        # self.load_path =roslib.packages.get_pkg_dir('intersection_detector') + '/data/model/lrcn/real/frame16/hz8/30ep/0911_right_add_area_ele_dai_temae_go/model_gpu.pt'

        self.save_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/model/lrcn/'
        
        self.save_image_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/center/image/'
        self.save_label_path = roslib.packages.get_pkg_dir('intersection_detector') + '/data/dataset/lrcn/center/label/'

        self.previous_reset_time = 0
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.pos_the = 0.0
        self.is_started = False
        self.cmd_dir_data = [0,0,0,0,0,0,0,0]
        self.intersection_list = ["straight_road","dead_end","corner_right","corner_left","cross_road","3_way_right","3_way_center","3_way_left"]
        self.start_time_s = rospy.get_time()
        # os.makedirs(self.path + self.start_time)

        self.target_dataset = 12000
        # print("target_dataset :" , self.target_dataset)
        # with open(self.path + self.start_time + '/' +  'training.csv', 'w') as f:
        #     writer = csv.writer(f, lineterminator='\n')
        #     writer.writerow(['step', 'mode', 'loss', 'angle_error(rad)', 'distance(m)','x(m)','y(m)', 'the(rad)', 'direction'])

    def callback(self, data):
        try:
            # self.cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            self.cv_image = self.bridge.imgmsg_to_cv2(data, "rgb8")
        except CvBridgeError as e:
            print(e)

    # def callback_left_camera(self, data):
    #     try:
    #         # self.cv_left_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
    #         self.cv_left_image = self.bridge.imgmsg_to_cv2(data, "rgb8")
    #     except CvBridgeError as e:
    #         print(e)

    # def callback_right_camera(self, data):
    #     try:
    #         # self.cv_right_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
    #         self.cv_right_image = self.bridge.imgmsg_to_cv2(data, "rgb8")
    #     except CvBridgeError as e:
    #         print(e)


    def callback_cmd(self, data):
        self.cmd_dir_data = data.intersection_label
        # rospy.loginfo(self.cmd_dir_data)
        # rospy.loginfo(self.cmd_dir_data)

    def callback_dl_training(self, data):
        resp = SetBoolResponse()
        # self.learning = data.data
        self.learning_tensor_flag = data.data
        resp.message = "Training: " + str(self.learning)
        resp.success = True
        return resp


    def loop(self):
        test_flag =False
        
        if self.learning_tensor_flag:
            # dataset ,dataset_num,train_dataset =self.dl.make_dataset(img,self.cmd_dir_data)
            # self.dl.training(train_dataset)

            # self.b2t.load(self.load_path)
            # print("load model: ",self.load_path)
            # print(self.load_image_path)
            # print(self.load_label_path)
            # x_tensor,t_tensor = self.b2t.cat_tensor(self.load_center_image_path,self.load_left_image_path,self.load_right_image_path,
            #                                         self.load_center_label_path,self.load_left_label_path,self.load_right_label_path)
            
            # x_tensor,t_tensor = self.b2t.cat_tensor(self.load_image_path_1,self.load_image_path_2,self.load_image_path_3,
            #                                         self.load_label_path_1,self.load_label_path_2,self.load_label_path_3)
            # x_tensor,t_tensor = self.b2t.cat_tensor_2(self.load_image_path_2,self.load_image_path_3,
                                                    # self.load_label_path_2,self.load_label_path_3)
            x_tensor, t_tensor = self.b2t.cat_tensor_9(self.load_image_path_1, self.load_image_path_2, self.load_image_path_3,
                                                        self.load_image_path_4, self.load_image_path_5, self.load_image_path_6,
                                                        self.load_image_path_7, self.load_image_path_8, self.load_image_path_9,
                                                        self.load_label_path_1, self.load_label_path_2, self.load_label_path_3,
                                                        self.load_label_path_4, self.load_label_path_5, self.load_label_path_6,
                                                        self.load_label_path_7, self.load_label_path_8, self.load_label_path_9)

            # x_tensor = self.load_image_path
            # t_tensor = self.load_label_path
            #show label info
            # self.b2t.tensor_info(x_tensor,t_tensor)
            # sys.exit()
            _,_ = self.b2t.cat_training(x_tensor, t_tensor, False)
            # _,_ = self.b2t.training(self.load_image_path,self.load_label_path)
            # self.b2t.save_bagfile(x_tensor,self.save_image_path,'/image.pt')
            # self.b2t.save_bagfile(t_tensor,self.save_label_path, '/label.pt')
            self.b2t.save(self.save_path)
            self.learning_tensor_flag = False
            print("Finish learning")
            # os.system('killall roslaunch')
            # sys.exit()
        # else :
        #     print("please start learning")
        if test_flag:
            self.b2t.load(self.load_path)
            # # print("load model: ",self.load_path)
            print(self.load_image_path)
            print(self.load_label_path)
            accuracy = self.b2t.model_test(self.load_image_path,self.load_label_path)
            os.system('killall roslaunch and test model')
            sys.exit()


if __name__ == '__main__':
    rg = intersection_detector_node()
    # DURATION = 0.1
    # r = rospy.Rate(1 / DURATION)
    # r= rospy.Rate(5.0)
    r = rospy.Rate(8.0)
    while not rospy.is_shutdown():
        rg.loop()
        r.sleep()
