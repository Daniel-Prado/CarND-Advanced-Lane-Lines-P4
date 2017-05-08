import numpy as np

class Line():
	def __init__(self, image_shape, window_h, window_w, My_ym = 40/720, My_xm = 3.7/700, smooth_factor=10):
		# was the line detected in the last iteration?
		self.detected = False  

		# x values of the last n fits of the line
		# self.recent_xfitted = [] 

		# list of recent fit polynom coefficients
		self.recent_fit = []

		# list of recent fit polynom coefficients, in meter units
		self.recent_fit_m = []

		#average x values of the fitted line over the last n iterations
		self.bestx = None     

		#polynomial coefficients averaged over the last n iterations
		self.best_fit = None  

		#polynomial coefficients for the most recent fit
		self.current_fit = None #[np.array([False])] 

		#polynomial coefficients for the most recent fit, in meter units
		self.current_fit_m = None 

		#radius of curvature of the line in meters units
		self.radius_of_curvature = None 

		#list of recent radius of curvature
		self.recent_line_curverad = []

		#distance in meters of vehicle center from the line
		#self.line_base_pos = None 

		#difference in fit coefficients between last and new fits
		#self.diffs = np.array([0,0,0], dtype='float') 

		#x values for detected line pixels
		#self.allx = None  

		#y values for detected line pixels
		#self.ally = None

		self.yvals = range(0, image_shape[0])
		self.res_yvals = np.arange(image_shape[0]-window_h/2, 0, -window_h)
		self.y_eval = np.max(self.yvals)

		self.window_height = window_h
		self.window_width = window_w

		self.lastx = None

		self.smooth_factor = smooth_factor

		self.xm_per_pix = My_xm
		self.ym_per_pix = My_ym


		return

	def update_centroids(self, centroids):
		## Assumes centroids is only LEFT or RIGHT

		self.lastx = np.copy(centroids)

		return

	def get_line_curvature(self):

		ym_per_pix = self.ym_per_pix
		xm_per_pix = self.xm_per_pix
		y_eval = self.y_eval

		fit_cr = self.best_fit_m
		self.radius_of_curvature = ((1 + (2*fit_cr[0]*y_eval*ym_per_pix + fit_cr[1])**2)**1.5) / np.absolute(2*fit_cr[0])

		self.recent_line_curverad.append(self.radius_of_curvature)

		if len(self.recent_fit) == 101:
			del self.recent_line_curverad[0]

		return np.average(self.recent_line_curverad[-100:], axis = 0)

	def line_fit(self):
		self.current_fit = np.polyfit(self.res_yvals, self.lastx, 2)
		self.current_fit_m = np.polyfit(self.res_yvals * self.ym_per_pix \
			, self.lastx * self.xm_per_pix, 2)

		self.recent_fit.append(self.current_fit)
		self.recent_fit_m.append(self.current_fit_m)

		if len(self.recent_fit) == self.smooth_factor + 1:
			del self.recent_fit[0]
			del self.recent_fit_m[0]

		self.best_fit = np.average(self.recent_fit[-self.smooth_factor:], axis=0)
		self.best_fit_m = np.average(self.recent_fit_m[-self.smooth_factor:], axis=0)
	
		fit = self.best_fit
		yvals = self.yvals
		self.line_fitx = np.array( fit[0]*yvals*yvals + fit[1]*yvals + fit[2], np.int32)
		
		self.detected = True

		return self.line_fitx, self.yvals

	def get_lane_for_drawing(self):
		line_fitx = self.line_fitx
		window_width = self.window_width
		yvals = self.yvals

		lane = np.array(list(zip(np.concatenate((line_fitx-window_width/2,line_fitx[::-1]+window_width/2), axis=0)
                                 ,np.concatenate((yvals,yvals[::-1]),axis=0))),np.int32)
		return lane

	


