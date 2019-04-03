# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 10:26:07 2018

@author: LELJD420
"""

import matplotlib as mpl
import scipy.stats as stats
import numpy as np
import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk
import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_agg import FigureCanvasAgg

from excelparsing import xlimpexp as xl


class Fitter(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.distro = None
        self.data_ordering = 'columns'
        
        # defaults
        self.bg_color = 'lavender'
        self.canvas_color = 'oldlace'
        default_filename_str = 'output.xlsx'
        default_col_str = 'data'
        default_col_idx_str = '1'
        default_distro_str = 'beta'
        default_bins_str = '10'
        default_hist_color_str = "steel blue"
        default_line_color_str = 'brick red'
        default_filegendistro_str = 'output.xlsx'
        default_samplesize_str = '10000'
        default_distro_param_str = '10,4'
        
        self.configure(bg = self.bg_color)
        
        w_d, h_d = 700, 700 #pixels
        distribution_frame = tk.LabelFrame(self, width=w_d, height=h_d, padx=5, pady=5, text="Distribution", bg=self.bg_color)
        distribution_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        w_s, h_s = 300, 400 #pixels
        settings_frame = tk.LabelFrame(self, width=w_s, height=h_s, padx=5, pady=5, text="Settings", bg=self.bg_color)
        settings_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        generate_frame = tk.LabelFrame(self, width=w_s, height=h_s, padx=5, pady=5, text="Generate", bg=self.bg_color)
        generate_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        w_c, h_c = 700, 700 #pixels 
        canvas = tk.Canvas(distribution_frame, width=w_c, height=h_c, bg=self.canvas_color)
        canvas.pack()
        
        #blank figure init
        self.fig = mpl.pyplot.figure(facecolor=self.canvas_color)
        self.fig_photo = self.draw_figure(canvas, self.fig)
        self.fig_w, self.fig_h = self.fig_photo.width(), self.fig_photo.height()
        canvas.configure(width=self.fig_w, height=self.fig_h, bg=self.canvas_color)
        
        w_l, h_l = 50, 3 #chars, lines
        label_param = tk.Label(distribution_frame, width=w_l, height=h_l, bg=self.bg_color)
        label_param.pack()
        
        self.label_samples_number = tk.Label(distribution_frame, width=w_l, height=h_l, bg=self.bg_color)
        self.label_samples_number.pack()
        
        w_f, h_f = 300, 50 #pixels
        filename_frame = tk.LabelFrame(settings_frame, width=w_f, height=h_f, padx=1, pady=1, text="File name", bg=self.bg_color)
        filename_frame.pack()
        
        self.colname_frame = tk.LabelFrame(settings_frame, width=w_f, height=h_f, padx=1, pady=1, text="Column header", bg=self.bg_color)
        self.colname_frame.pack()
        
        distroname_frame = tk.LabelFrame(settings_frame, width=w_f, height=h_f, padx=1, pady=1, text="Distribution", bg=self.bg_color)
        distroname_frame.pack()       
        
        bins_frame = tk.LabelFrame(settings_frame, width=w_f, height=h_f, padx=1, pady=1, text="Bins", bg=self.bg_color)
        bins_frame.pack()
        
        w_t = 20 #chars
        filename = tk.StringVar()
        text_filename = tk.Entry(filename_frame, width=w_t, textvariable=filename)
        text_filename.pack()
        text_filename.delete(0, tk.END)
        text_filename.insert(0, default_filename_str)
        
        self.bins_distro = tk.IntVar()
        text_bins = tk.Entry(bins_frame, width=w_t, textvariable=self.bins_distro)
        text_bins.pack()
        text_bins.delete(0, tk.END)
        text_bins.insert(0, default_bins_str)
        
        w_ck, h_ck = 10, 1 #chars, lines
        self.col_row_flag = tk.IntVar() # =1 if the button is selected
        check_col_row = tk.Checkbutton(self.colname_frame, width=w_ck, height=h_ck, padx=1, pady=1, text="Rows", variable=self.col_row_flag, command=self.check_row, bg=self.bg_color)
        check_col_row.pack()
        
        col_name = tk.StringVar()
        text_col = tk.Entry(self.colname_frame, width=w_t, textvariable=col_name)
        text_col.pack()
        text_col.delete(0, tk.END)
        text_col.insert(0, default_col_str)
        
        self.col_name_idx = tk.StringVar()
        text_col_idx = tk.Entry(self.colname_frame, width=w_t, textvariable=self.col_name_idx)
        text_col_idx.pack()
        text_col_idx.delete(0, tk.END)
        text_col_idx.insert(0, default_col_idx_str)
        
        distro_name = tk.StringVar()
        text_distro = tk.Entry(distroname_frame, width=w_t, textvariable=distro_name)
        text_distro.pack()
        text_distro.delete(0, tk.END)
        text_distro.insert(0, default_distro_str) #default distro is normal distro
        
        
        w_ck, h_ck = 10, 1 #chars, lines
        weight_flag = tk.IntVar() # =1 if the button is selected
        check_weight = tk.Checkbutton(settings_frame, width=w_ck, height=h_ck, padx=1, pady=1, text="Weighted", variable=weight_flag, bg=self.bg_color)
        check_weight.pack()
        
        
        w_b, h_b = 10, 1 #chars, lines
        button_update = tk.Button(settings_frame, width=w_b, height=h_b, padx=1, pady=1, text="Update", command=lambda: self.fit_distro(filename.get(), col_name.get(), distro_name.get(), weight_flag.get(), canvas, label_param))
        button_update.pack()
        
        
        graphcolor_frame = tk.LabelFrame(settings_frame, width=w_f, height=h_f, padx=1, pady=1, text="Colors", bg=self.bg_color)
        graphcolor_frame.pack()
        
        savepic_frame = tk.LabelFrame(settings_frame, width=w_f, height=h_f, padx=1, pady=1, text="Save Picture", bg=self.bg_color)
        savepic_frame.pack()
        
        
        w_t = 20 #chars
        self.line_color = tk.StringVar()
        text_linecolor = tk.Entry(graphcolor_frame, width=w_t, textvariable=self.line_color)
        text_linecolor.pack()
        text_linecolor.delete(0, tk.END)
        text_linecolor.insert(0, default_line_color_str)
        
        self.hist_color = tk.StringVar()
        text_histcolor = tk.Entry(graphcolor_frame, width=w_t, textvariable=self.hist_color)
        text_histcolor.pack()
        text_histcolor.delete(0, tk.END)
        text_histcolor.insert(0, default_hist_color_str)
        
        self.counter_picname = 1
        self.pic_name = tk.StringVar()
        self.text_savepic = tk.Entry(savepic_frame, width=w_t, textvariable=self.pic_name)
        self.text_savepic.pack()
        self.text_savepic.delete(0, tk.END)
        self.text_savepic.insert(0, 'pic%i' % self.counter_picname)
        self.pic_name_old = self.pic_name.get().rstrip('0123456789')
        
        
        w_b, h_b = 10, 1 #chars, lines
        button_save = tk.Button(savepic_frame, width=w_b, height=h_b, padx=1, pady=1, text="Save", command=lambda: self.save_pic(self.fig))
        button_save.pack()
        
        
        outputxlsx_frame = tk.LabelFrame(generate_frame, width=w_f, height=h_f, padx=1, pady=1, text="File name", bg=self.bg_color)
        outputxlsx_frame.pack()
        
        size_frame = tk.LabelFrame(generate_frame, width=w_f, height=h_f, padx=1, pady=1, text="Size", bg=self.bg_color)
        size_frame.pack()
        
        param_frame = tk.LabelFrame(generate_frame, width=w_f, height=h_f, padx=1, pady=1, text="Parameters", bg=self.bg_color)
        param_frame.pack()
        
        filegendistro_name = tk.StringVar()
        text_filegendistro = tk.Entry(outputxlsx_frame, width=w_t, textvariable=filegendistro_name)
        text_filegendistro.pack()
        text_filegendistro.delete(0, tk.END)
        text_filegendistro.insert(0, default_filegendistro_str) 
        
        samplesize = tk.StringVar()
        text_samplesize = tk.Entry(size_frame, width=w_t, textvariable=samplesize)
        text_samplesize.pack()
        text_samplesize.delete(0, tk.END)
        text_samplesize.insert(0, default_samplesize_str)
        
        distro_param_str = tk.StringVar()
        text_samplesize = tk.Entry(param_frame, width=w_t, textvariable=distro_param_str)
        text_samplesize.pack()
        text_samplesize.delete(0, tk.END)
        text_samplesize.insert(0, default_distro_param_str)
        
        button_gendata = tk.Button(generate_frame, width=w_b, height=h_b, padx=1, pady=1, text="Generate", command=lambda: self.generate_data(distro_name.get(), filegendistro_name.get(), col_name.get(), int(samplesize.get()), tuple(distro_param_str.get().split(sep=','))))
        button_gendata.pack()
    
    def draw_figure(self, canvas, figure, loc=(0, 0)):
        """ 
        Draw a matplotlib figure onto a Tk canvas    
        loc: location of top-left corner of figure on canvas in pixels.
        Inspired by matplotlib source: lib/matplotlib/backends/backend_tkagg.py
        """
        figure_canvas_agg = FigureCanvasAgg(figure)
        figure_canvas_agg.draw()
        figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds
        figure_w, figure_h = int(figure_w), int(figure_h)
        photo = tk.PhotoImage(master=canvas, width=figure_w, height=figure_h)
    
        # Position: convert from top-left anchor to center anchor
        canvas.create_image(loc[0] + figure_w/2, loc[1] + figure_h/2, image=photo)
    
        # Unfortunately, there's no accessor for the pointer to the native renderer
        tkagg.blit(photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)
    
        # Return a handle which contains a reference to the photo object
        # which must be kept live or else the picture disappears
        return photo
    
    def fit_distro(self, file_n, col_n, distro_n, w_flag, canvas, params_parent):
        aa = xl(importedfilename=file_n)
        dataa = aa.importcolumn([col_n], data_ordering=self.data_ordering)
#        print(dataa)
        y = dataa[col_n][int(self.col_name_idx.get())-1]
        
        mpl.pyplot.close(self.fig)
        self.fig, self.ax = mpl.pyplot.subplots(1,1)
        
        distro = getattr(stats, distro_n)
        self.distro=distro
        
        delta_x = max(y)-min(y)
        x = np.linspace(min(y)-delta_x/5, max(y)+delta_x/5, 100)
        # fit
        param = distro.fit(y)
        pdf_fitted = distro.pdf(x, *param)
        mpl.pyplot.plot(x, pdf_fitted, color='xkcd:'+self.line_color.get())
        
        if w_flag:
            weights = np.ones_like(y)/float(len(y))
            n, bins, patches = mpl.pyplot.hist(y, weights=weights, bins=self.bins_distro.get(), color='xkcd:'+self.hist_color.get())
        else:
            n, bins, patches = mpl.pyplot.hist(y, normed=True, bins=self.bins_distro.get(), color='xkcd:'+self.hist_color.get())
        
        # Keep this handle alive, or else figure will disappear
        fig_x, fig_y = 1, 1
        self.fig_photo = self.draw_figure(canvas, self.fig, loc=(fig_x, fig_y))
        
        for child in params_parent.winfo_children():
            child.destroy()
        
        label_param_list = [];
        for i in range(len(param)):
            label_param_list.append(tk.Label(params_parent))
            label_param_list[i].configure(text="Parameter %i = %f" % (i+1, param[i]), bg=self.bg_color)
            label_param_list[i].pack(side=tk.LEFT)
        
        self.label_samples_number.configure(text="Sample set size: %i" % len(y))
        return
     
    def save_pic(self, picture):
        picture.savefig(self.pic_name.get())        
        pic_name_str = self.pic_name.get().rstrip('0123456789')     # strip charcaters from end of string
        if self.pic_name_old == pic_name_str:
            self.counter_picname += 1
        else:
            self.counter_picname = 1
        self.text_savepic.delete(0, tk.END)
        self.text_savepic.insert(0, pic_name_str+'%i' % self.counter_picname)
        self.pic_name_old = pic_name_str
        return
    
    def check_row(self):
        if self.col_row_flag.get() == 1:
            self.colname_frame.configure(text='Row header')
            self.data_ordering = 'rows'
        else:
            self.colname_frame.configure(text='Column header')
            self.data_ordering = 'columns'
        return
            
    def generate_data(self, distro_name, filename, colname, size, args_str):
        distro = getattr(stats, distro_name)
        if args_str == tuple(['']):
            data = distro.rvs(size=size)
        else:
            args = tuple([int(x) for x in args_str])
            data = distro.rvs(size=size, *args)
        bb = xl(exportedfilename=filename)
        bb.exportlist(data)
        return

MainWindow = Fitter(None)
MainWindow.title("Fitter")
MainWindow.mainloop()
distro = MainWindow.distro