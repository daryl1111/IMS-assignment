import shlex
import subprocess
import time
import re
import matplotlib.pyplot as plt

#import cmd command
def cmd(cmd):
   process=subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
   out=process.stdout.readlines()
   time.sleep(2)
   return out

#Obtain video resolution
def GetResolution(filename):
    resolution_out=cmd('ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 %s'%filename)
    resolution=resolution_out[0].decode().strip()
    return resolution

#Perform H.265 encoding
def x265encoding(filename,bitrate,speed):
    cmd('./ffmpeg -i %s -c:v libx265 -b %s -preset %s %s_%s.mp4'%(filename,bitrate,speed,bitrate,speed))

#Convert video format
def YUVconversion(filename,bitrate,speed):
    cmd('ffmpeg -i %s_%s.mp4 %s_%s_dec.yuv'%(bitrate,speed,bitrate,speed))
    cmd('ffmpeg -i %s %s_%s_ori.yuv'%(filename,bitrate,speed))

#Measure PSNR
def psnr(resolution,filename,bitrate,speed):
   cmd('./ffmpeg -s %s -i %s_%s_dec.yuv -s %s -i %s_%s_ori.yuv -lavfi psnr="stats_file=%s_%s_psnr.log" -f null -'%(resolution,bitrate,speed,resolution,bitrate,speed,bitrate,speed))
   PSNR_Per_Frame=[]
   psnrfile=open('%s_%s_psnr.log'%(bitrate,speed),'r') #Search PSNR result
   for line in psnrfile:
       temp=re.findall(r"\d+\.?\d*",line)
       SinglePSNR=float(temp[5])
       PSNR_Per_Frame.append(SinglePSNR)
   psnrfile.close()
   num=0
   for i in range(len(PSNR_Per_Frame)): #calculate average PSNR
       num+=PSNR_Per_Frame[i]
   AverPSNR=num/len(PSNR_Per_Frame)    
   return AverPSNR

#Measure SSIM
def ssim(resolution,filename,bitrate,speed):
   cmd('./ffmpeg -s %s -i %s_%s_dec.yuv -s %s -i %s_%s_ori.yuv -lavfi ssim="stats_file=%s_%s_ssim.log" -f null -'%(resolution,bitrate,speed,resolution,bitrate,speed,bitrate,speed))
   SSIM_Per_Frame=[]
   ssimfile=open('%s_%s_ssim.log'%(bitrate,speed),'r') #Search PSNR result
   for line in ssimfile:
       temp=re.findall(r"\d+\.?\d*",line)
       SingleSSIM=float(temp[4])
       SSIM_Per_Frame.append(SingleSSIM)
   ssimfile.close()
   num=0
   for i in range(len(SSIM_Per_Frame)): #calculate average SSIM
       num+=SSIM_Per_Frame[i]
   AverSSIM=num/len(SSIM_Per_Frame)    
   return AverSSIM

#Measure VMAF     
def vmaf(filename,bitrate,speed):
    out=cmd('./ffmpeg -i %s_%s.mp4 -i %s -lavfi libvmaf="model_path=./model/vmaf_v0.6.1.pkl:psnr=1:log_fmt=json" -f null -'%(bitrate,speed,filename))
    VAMFencode=out[2]
    VAMFdecode=re.findall(r"\d+\.?\d*",VAMFencode.decode().strip())
    VAMFout=float(VAMFdecode[0])
    return VAMFout 

#perform video test
def videotest(filename,testtime,bitrate,speed,resolution):
    x265encoding(filename,bitrate,speed)
    YUVconversion(filename,bitrate,speed)
    Vmaf=vmaf(filename,bitrate,speed)
    Psnr=psnr(resolution,filename,bitrate,speed)
    Ssim=ssim(resolution,filename,bitrate,speed)
    print('----------------Sample%i Results------------------------'%testtime)
    print('vamf: %f'%Vmaf)
    print('psnr: %f'%Psnr)
    print('ssim: %f'%Ssim)
    tune=[Vmaf,Psnr,Ssim]
    print('--------------------------------------------------------')
    return tune

#ask for input
filename=input('File name:')
Testtimes=int(input('Please enter test times:'))
print('Please set testing parameters for each time')
print('eg. Bitrate:20k, Speed:slow, crf:22')
bitratelist=[]
speedlist=[]

for i in range(Testtimes):
    sample=i+1
    bitrate=input('Sample %i--Bitrate:'%sample)
    bitratelist.append(bitrate)
    speed=input('          --Speed:')
    speedlist.append(speed)
    
VideoResolution=GetResolution(filename)


#start test
vmaftest=[]
psnrtest=[]
ssimtest=[]
for i in range(Testtimes):
    testtime=i+1
    bitrate=bitratelist[i]
    speed=speedlist[i]
    
    resolution=VideoResolution
    tunetemp=videotest(filename,testtime,bitrate,speed,resolution)
    vmaftest.append(tunetemp[0])
    psnrtest.append(tunetemp[1])
    ssimtest.append(tunetemp[2])

#display result
print('vmaf:',vmaftest)
print('psnr:',psnrtest)
print('ssim:',ssimtest)

#display plot
plotselect=int(input('Please Slect the plot--1.Bitrate plot--2.Speed plot--3.Crf plot :'))
if plotselect==1:
    plt.plot(bitratelist,psnrtest)
    plt.ylabel('PSNR')
    plt.xlabel('Bitrate')
    plt.title('Bitrate VS PSNR')
    plt.show()
    
    plt.plot(bitratelist,ssimtest)
    plt.ylabel('SSIM')
    plt.xlabel('Bitrate')
    plt.title('Bitrate VS SSIM')
    plt.show()

    plt.plot(bitratelist,vmaftest)
    plt.ylabel('VMAF')
    plt.xlabel('Bitrate')
    plt.title('Bitrate VS VMAF')
    plt.show()

elif plotselect==2:
    plt.plot(speedlist,psnrtest)
    plt.ylabel('PSNR')
    plt.xlabel('Speed')
    plt.title('Speed VS PSNR')
    plt.show()
    
    plt.plot(speedlist,ssimtest)
    plt.ylabel('SSIM')
    plt.xlabel('Speed')
    plt.title('Speed VS SSIM')
    plt.show()

    plt.plot(speedlist,vmaftest)
    plt.ylabel('VMAF')
    plt.xlabel('Speed')
    plt.title('Speed VS VMAF')
    plt.show()












