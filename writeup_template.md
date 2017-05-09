# **Advanced Lane Finding Project**
#### by Daniel Prado Rodriguez
#### Udacity SDC Nanodegree. Feb'17 Cohort.
---
The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

[//]: # (Image References)

[image1]: ./examples/undistort_output.png "Undistorted"
[image2]: ./test_images/test1.jpg "Road Transformed"
[image3]: ./output_images/binary1.jpg "Binary Thresholded image"
[image4.1]: ./output_images/straight_binary2.jpg "Binary Straight lines"
[image4.2]: ./output_images/straight_warped2.jpg "Warped Straight lines"
[image5.1]: ./output_images/sidewin6.jpg "Detected centroids showing the sliding windows (green)"
[image5.2]: ./examples/color_fit_lines.jpg "Fit Visual"
[image6]: ./output_images/result6.jpg "Output result"
[video1]: ./project_video.mp4 "Video"

## [Rubric](https://review.udacity.com/#!/rubrics/571/view) Points

Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---

### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  [Here](https://github.com/udacity/CarND-Advanced-Lane-Lines/blob/master/writeup_template.md) is a template writeup for this project you can use as a guide and a starting point.  

You're reading it!

### Camera Calibration

#### 1. Briefly state how you computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image.

The code for this step is contained in two code cells in my Python notebook, under section "Step 1. Camera Calibration", located in "./advanced_lane_lines.ipynb".

I start by preparing "object points", which will be the (x, y, z) coordinates of the chessboard corners in the world. Here I am assuming the chessboard is fixed on the (x, y) plane at z=0, such that the object points are the same for each calibration image.  Thus, `objp` is just a replicated array of coordinates, and `objpoints` will be appended with a copy of it every time I successfully detect all chessboard corners in a test image.  `imgpoints` will be appended with the (x, y) pixel position of each of the corners in the image plane with each successful chessboard detection.  The images of the corners detected in this process are briefly shown on screen (outside of the notebook) and also written to disk as "output_images/corners_found(id).jpg"

In then second cell, I then use the output `objpoints` and `imgpoints` to compute the camera calibration and distortion coefficients using the `cv2.calibrateCamera()` function.  I applied this distortion correction to the test image using the `cv2.undistort()` function and obtained this result: 

![alt text][image1]

### Pipeline (single images)

#### 1. Provide an example of a distortion-corrected image.

To demonstrate this step, I will describe how I apply the distortion correction to one of the test images like this one. Implementation can be found in section "Step 2. Applying Distorsion Correction" of the IPython notebook.
![alt text][image2]

#### 2. Describe how (and identify where in your code) you used color transforms, gradients or other methods to create a thresholded binary image.  Provide an example of a binary image result.

The thresholded binary image creation is implemented in "Step 3. Color & Gradient Thresholds --> Binary Image" of the notebook. The first two cells defines subfunctions for the different thresholds and a main function `detect_line_borders` that will be used both for the single images and for the video pipeline.
I used a combination of color and gradient thresholds to generate a binary image.
This combination is a logical OR of 3 thresholds:
* Color Threshold, for component S>105 and component V>205, int he HSV and HSL colorspaces, respectively.
* Gradient Threshold X (>12) AND Gradient Threshold Y (>25)
* Magnitude (>10) AND Direction Gradient Threshold between 0.85 and 1.15 rad.

Here's an example of my output for this step.  (note: this is not actually from one of the test images)

![alt text][image3]

#### 3. Describe how (and identify where in your code) you performed a perspective transform and provide an example of a transformed image.

The code for my perspective transform includes a function called `perspective_transform_warp()`, which appears in Section 4 of the IPython notebook (advanced_lane_lines.ipynb) .  The `perspective_transform_warp()` function takes as inputs an image (`img`), as well as source (`src`) and destination (`dst`) points.  I chose the hardcode the source and destination points in the following manner:

| Source        | Destination   | 
|:-------------:|:-------------:| 
| 593, 450      | 320, 0        | 
| 691, 450      | 960, 0        |
| 260, 684      | 320, 720      |
| 1070, 684     | 960, 720      |

I verified that my perspective transform was working as expected by drawing the `src` and `dst` points onto a test image and its warped counterpart to verify that the lines appear parallel in the warped image.

Binary image, before warping:
![alt text][image4.1]

After Warping:
![alt text][image4.2]

#### 4. Describe how (and identify where in your code) you identified lane-line pixels and fit their positions with a polynomial?

After getting the binary warped images, the next step is to detect the lines. In order to do so, I used the sliding window convolution method.
This method is implemented in a class named `Tracker`, in a separate python file `tracker.py`, that is then imported in the IPython notebook (see code cell under Section 5).

By this method the image is divided into 9 rows of the same height (80 pixels). For every row, every column of binary pixels is summed, hence obtanining a one-dimensional signal.
This one-dimensional signal is convolved with a square window of a predetermined width, and as a result, we get 1 peak in the left-hand side of the image and another peak in the right-hand side.
Actually, the position of the peaks in the lower row of the image is determined using the lower quarter of the image, and not only the 80-pix row. This is because we need to make sure that the position of the lower row in the frame is valid, as the following rows are searched only within a margin of the previous one.

As a result, this process gives a list of 9 centroids for every side of the image, left and right. Below we can see a sample of this intermediate result:

![alt text][image5.1]

The next sub-step is to fit one 2nd degree polynom function based on the previous calculated centroids, for both lane lines.
This is implemented in a class named `Line` in a separate python file `file.py`, that is then imported in the IPython notebook (see code cell under Section 5).

![alt text][image5.2]

Next, with the obtained polynom coeficients, we can draw the lines over a blank bird-eye frame, the left line in red, and right line in blue, and fill-in the lane in-between in green color.

Finally, we unwarp this image to the original perspective, using the `perspective_transform_unwarp` function. The resulting image is added to the original (lens-undistorted) image.


#### 5. Describe how (and identify where in your code) you calculated the radius of curvature of the lane and the position of the vehicle with respect to center.

The calculation of the radius of curvature is done in the method `get_line_curvature` of my Line class in file `line.py`. 
I apply the formula we have seen in the lessons to obtain the curve of a polynomic function at a given point based on its coeficients. I apply the factor of 40m/720 pixels to get the result in meters and not in pixels.
Actually this method calculates the curvature of one of the lines (left or right), and then I average both results in my notebook to get the radius of the curve.

#### 6. Provide an example image of your result plotted back down onto the road such that the lane area is identified clearly.

The complete pipeline explained before in the section 4 gives as a result a picture like this:

![alt text][image6]

---

### Pipeline (video)

#### 1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

Here's a [link to my video result](./output_video.mp4)

---

### Discussion

#### 1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.  

The approach used has been described in enough detail in previous section of this report.
Special consideration must be given to the smoothing applied in the video pipeline (this has no effect in the static image pipeline).
I have used smoothing in two different parts of the process:
* Sliding window centroids detection: the position of each centroid is averaged with the 15 latests centroids at that y-position, in the previous 15 frames.
* Smoothing of the 2nd order Polynom coeficients. The coeficients of the polynom functions are also smoothed across the latest 10 frames.
* Smoothing of the curvature radius.. The calculation of the radius is obviously not very precise, so to avoid the jitter, I average the radius over the last 100 frames.

This degree of smoothing is acceptable, taking into account that the video is 30 Frames per second, the smoothing is only 1/2 and 1/3 of a second. For the radius the smoothing is maybe a bit too much, but radius in the kind of highway in the video don't change quickly anyway.
These tuning parameters would probably not be acceptable for other more challenging videos with quick turns.

Another aspect I would like to highlight is the importance of a fine-tuning in the binary thresholds. Although my thresholded images look a bit noisy, I found out that this provided a better result that if I lowered the thresholds to obtain a cleaner binary image, because in that case I tended to loose detail of the lines in the upper part of the scene.



