
Project:  Gaze Interaction for Everybody

Date:     Jan 2011       

Release version: 20121020

Purpose:    In this folder is stored the face database created for the project.

Contents:   The database has two folders. 
1.- The folder "images" contains the image files of the database. 
Each image file is named as follows: xxx_yy.png (xxx=user number, yy= image number). Each user has 12 images. There are 103 users.
2.- The folder "labels" contains the files with the coordinates of the labels for each image. The information is presented in two ways. 
In the first one, the labels of the user xxx is stored in a individual file named xxx_image_labels.txt. 
The format of these files is:
xxx_yy.png	x1 y1 x2 y2 x3 y3 x4 y4 x5 y5 x6 y6
The first point (x1,y1) is the external corner of the left user's eye. The second point is the centre of the left iris. 
The third one is the internal corner of the left eye. The other three points are internal corner, iris centre and 
external corner of the right eye. 

Also, as alternative way, all this information has been stored in a single file named image_labels.txt, containing the information 
of the 103 users and its format is the same one that has been described previously.

