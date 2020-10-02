"""
BSD 3-Clause License

Copyright (c) 2020, vj-sarthy
All rights reserved.

@Author: Vijay Sarthy, Ph.D., Mechanical Engineering, Clemson University, USA
@Email: vsreedh@g.clemson.edu


Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.'


Python code to determine the Gas Exchange Threshold (GET) from an cardiopulmonary exercise test.

Preparing the data, Please make sure that:
1. Time is on column 1 and is expressed in multiples of 10 and not as 0:10, 0:20, and so on...
2. vo2 data is on column 2 and vco2 data is on column 3 in the approapriate excel file.
Eg: If your sheet is named as Iron Man, please type 'Iron Man' instead of 'Sheet1'


"""

import os
import click
import pandas as pd
import glob
import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import tempfile

class GET(object):
    # window of data around threshold
    
    def __init__(self):
        self.threshold = None
        self.timestamp = None
        self.slope = None
        # linear regression co-efficients
        self.lcf = None
        # quadratic regression co-efficients 
        self.qcf = None
        # linear regression of left clipped data
        self.lcf_left = None
        # linear regression of right clipped data
        self.lcf_right = None
    
    def parse(self, file):
        st = pd.read_excel(file, "Sheet1")
        self.time = st['t'].values.tolist()
        self.vo2 = st['VO2'].values.tolist()
        self.vco2 = st['VCO2'].values.tolist()

    def compute(self):
        '''
        1. fit quadratic curve
        2. fit linear curve
        3. find point on quadratic curve which is at the max perpendicular distance from the linear curve 
        4. clip data from this point towards the start and end
        5. fit linear curves to two sets of data
        6. find the slopes and compute difference
        7. pick the point of Gas Exchange Threshold
        '''                
        # Converting lists into numerical arrays
        time = np.array(self.time)
        vo2  = np.array(self.vo2)
        vco2  = np.array(self.vco2)
        
        # Fitting a quadratic curve to the data
        self.qcf = np.polyfit(vo2,vco2,2)
        self.lcf = np.polyfit(vo2,vco2,1)
                
        # Extracting coeff of quadratic regression
        a, b, c = self.qcf[0], self.qcf[1], self.qcf[2]
        
        # Extracting coeff of linear regression
        m, C = self.lcf[0], self.lcf[1]

        # Distance between two regressions is maximum when the tangent to the quadratic model is parallel to the linear modelnear regression
        # Differentiating the the quadratic model will yield the tangent, i.e. slope m
        # Finding the point at which the tangent of the quadratic curve is parallel to the linear regression
        X = (m-b)/(2*a)
        Y = ((a*X**2)+(b*X)+c)
        
        diff = np.abs(self.vo2-X)
        diff_ind = diff.argmin()
        self.threshold = self.vo2[diff_ind]
        self.timestamp = time[diff_ind]
        
        # Determining the length of vo2 array
        k = len(vo2)
              
        # Creating two arrays: 1) all points before (X,Y) and 2) all points after (X,Y)
        vo2n1, vco2n1, vo2n2, vco2n2 = np.zeros(k), np.zeros(k), np.zeros(k), np.zeros(k)
        
        for i in range(k):
            if vo2[i]<=X:
                vo2n1[i], vco2n1[i] = vo2[i], vco2[i]
            else:
                vo2n2[i], vco2n2[i] = vo2[i], vco2[i]
        
        ind2 = np.nonzero(vo2n1)
        self.vo2nw1, self.vco2nw1 = vo2n1[ind2], vco2n1[ind2]
        
        ind3 = np.nonzero(vo2n2)
        self.vo2nw2, self.vco2nw2 = vo2n2[ind3], vco2n2[ind3]
        
        self.lcf_left = np.polyfit(self.vo2nw1, self.vco2nw1,1)
        self.lcf_right = np.polyfit(self.vo2nw2, self.vco2nw2,1)
        
        m3, C3 = self.lcf_left[0], self.lcf_left[1]        
        m4, C4 = self.lcf_right[0], self.lcf_right[1]
        self.slope = m4-m3
        
    def display(self):
        print('The Gas Exchange Threshold (GET) is:', self.threshold)
        print('The time stamp for Gas Exchange Threshold (GET) is:', self.timestamp)
        print('The difference between the two slopes is:', self.slope)
        
    def plot(self):
        Yplt_l, Yplt_q = np.poly1d(self.lcf), np.poly1d(self.qcf)
        
        # Size of the arrays before and after X
        p, q = len(self.vo2nw1), len(self.vo2nw2)
        
        # Extracting the coefficients of lower and upper linear regressions        
        Yplt_3, Yplt_4 = np.poly1d(self.lcf_left), np.poly1d(self.lcf_right)
        
        # Calculating y1 and y2 are for linear models and quadratic models
        
        # min and max of the VO2 array
        mn = min(self.vo2)
        mx = max(self.vo2)
        #creating an array of equally spaced data points between min and max of VO2
        x1 = np.linspace(mn, mx, 500)
        #print(x1)
        y1, y2 = Yplt_l(x1), Yplt_q(x1)
        
        # Initializing arrays for plotting
        # y3 and y4 are for the two linear models before and after X
        y3, y4 = np.zeros(p), np.zeros(q)
          
        # Calculating y3 and y4 using two for loops as the len of data points before and after X are not equal
        for i in range(p):
            y3[i] = Yplt_3(self.vo2nw1[i])
        for i in range(q):
            y4[i] = Yplt_4(self.vo2nw2[i])
            
        # Plotting two figures and saving them as jpeg files
        
        # Scatter plot
        plt.title("VCO2 v VO2")
        plt.xlabel("VO2")
        plt.ylabel("VCO2")
        plt.plot(self.vo2, self.vco2, '.')
        plt.savefig(os.path.join(tempfile.gettempdir(), "scatter.jpg"))
        
        # Plotting teh linear and the quadratic curves
        plt.title("VCO2 v VO2")
        plt.xlabel("VO2")
        plt.ylabel("VCO2")
        plt.plot(x1, y1, x1, y2, self.vo2, self.vco2, '.')
        plt.savefig(os.path.join(tempfile.gettempdir(), "lin_quad.jpg"))
        
        # Plotting the upper and the lower regressions
        plt.figure()
        plt.title("VCO2 v VO2 Split graph")
        plt.xlabel("VO2")
        plt.ylabel("VCO2")
        plt.plot(self.vo2nw1, y3, self.vo2nw2, y4, self.vo2, self.vco2, '.')
        plt.savefig(os.path.join(tempfile.gettempdir(), "lwr_upr_reg.jpg"))

    def sendmail(self):
        smtp_server = "smtp.gmail.com"
        stmp_port = 465
        from_addr = "pret.email2020@gmail.com"
        to_addr = input("Please enter your email address to send the GET plots: ")
        subject = "VCO2 vs VO2 plots"
        mail_body = "Please find the plots attached."
        attch_1 = os.path.join(tempfile.gettempdir(), "scatter.jpg")
        attch_2 = os.path.join(tempfile.gettempdir(), "lin_quad.jpg")
        attch_3 = os.path.join(tempfile.gettempdir(), "lwr_upr_reg.jpg")

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['To'] = to_addr
        msg.attach(MIMEText(mail_body))

        files = []
        files.append(attch_1)
        files.append(attch_2)
        files.append(attch_3)

        for file in files:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(file,"rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition','attachment; filename="{0}"'.format(os.path.basename(file)))
            msg.attach(part)
    
        try:
            server = smtplib.SMTP_SSL(smtp_server, stmp_port)
            server.login("pret.email2020", "Pass12342020")
            server.sendmail(from_addr, to_addr, msg.as_string())
            server.quit()
            text = "The email was sent! Please check your inbox."
            os.unlink(os.path.join(tempfile.gettempdir(), "scatter.jpg"))
            os.unlink(os.path.join(tempfile.gettempdir(), "lin_quad.jpg"))
            os.unlink(os.path.join(tempfile.gettempdir(), "lwr_upr_reg.jpg"))
        except:
            text = "Email sending failed. Please check the email address!"

        print(text)



@click.command()
@click.argument('xlsfilepath')
def main(xlsfilepath):
    results = []
    if os.path.isfile(xlsfilepath):
        '''Compute threshold'''
        try:
            obj = GET()
            obj.parse(xlsfilepath)
            obj.compute()
            obj.display()
            results.append([xlsfilepath.split("\\")[-1], obj.threshold, obj.timestamp, obj.slope])
            obj.plot()
            obj.sendmail()
        except Exception as e:
            print("Error while processing data file: {}, error: {}. Please correct the file.".format(excelfile, e))
    else:
         # Path to folder containing excel files
        print("Searching for data files in the directory: {}".format(xlsfilepath))
       
        # set all .xls files in your folder to list
        allfiles = glob.glob(xlsfilepath + "\*.xlsx")

        # for loop to aquire all excel files in folder
        
        for excelfile in allfiles:
            '''Compute threshold'''
            try:
                print("Processing file: {}".format(excelfile))
                obj = GET()
                obj.parse(excelfile)
                obj.compute()
                obj.plot()
                obj.sendmail()
                results.append([excelfile.split("\\")[-1], obj.threshold, obj.timestamp, obj.slope])
            except Exception as e:
                print("Error while processing data file: {}, error: {}. Please correct the file.".format(excelfile, e))
    print(tabulate(results, headers=["File", "GET", "Timestamp", "Slope difference"]))

if __name__ == '__main__':
    main()



