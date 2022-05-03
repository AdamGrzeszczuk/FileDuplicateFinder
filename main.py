import tkinter.filedialog
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import ImageTk, Image, ExifTags
import os
import time
import fnmatch
import pyheif
import subprocess
import platform
import magic
import cv2
import datetime
import time

class Duplicates:

    def __init__(self, master):

        self.time_start = 0

        master["bg"] = "#D3E4CD"
        master.config(padx=20, pady=20)
        master.minsize(width=780, height=750)
        master.title(" Pic Duplicates")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", background="#E2C2B9")
        self.style.configure("TFrame", background="#D3E4CD")
        self.style.configure("TLabel", background="#D3E4CD")
        self.style.configure("TRadiobutton", background="#D3E4CD")


        self.header_frame = ttk.Frame(master)
        self.header_frame.pack()

# creating app layout
        lbSystem = ttk.Label(self.header_frame, text="Select Operating System:", font='default 10 bold', background="#D3E4CD")
        lbSystem.grid(row=0, column=0)
        self.var = IntVar()
        self.rbSystemLinux = ttk.Radiobutton(self.header_frame, text="Linux", variable=self.var, value=0)
        self.rbSystemLinux.grid(row=0, column=1)
        self.rbSystemLinux = ttk.Radiobutton(self.header_frame, text="Windows", variable=self.var, value=1)
        self.rbSystemLinux.grid(row=0, column=2)

        lbDirectory = ttk.Label(self.header_frame, text="Select directory:", font='default 10 bold', background="#D3E4CD")
        lbDirectory.grid(row=1, column=0)

        self.select_frame = ttk.Frame(master)
        self.select_frame.pack()

        self.enDirectory = ttk.Entry(self.select_frame, width=80, font=("default", 10), background="#F2DDC1")
        self.enDirectory.insert(END, string="Type the path here or select it with a button.")
        self.enDirectory.grid(row=2, column=0, padx=5, pady=5)
        
        btSelectDir = ttk.Button(self.select_frame, text="Select folder", command=self.select_folder) #select_folder)
        btSelectDir.grid(row=2, column=1, padx=5, pady=5)

        btScan = ttk.Button(self.select_frame, text="Scan directory", command=self.scan)
        btScan.grid(row=2, column=2, padx=5, pady=5)

        self.files_frame = ttk.Frame(master)
        self.files_frame.pack()

        self.lbFiles = ttk.Label(self.files_frame, text="Files and duplicates:", font="default 10 bold", background="#D3E4CD")
        self.lbFiles.grid(row=0, column=0)

        self.lbFilesList = Listbox(self.files_frame, height=9, width=50, bg="#F2DDC1")
        self.lbFilesList.grid(row=1, column=0, columnspan=2)

        self.scrollbar = Scrollbar(self.files_frame)
        self.scrollbar.grid(row=1, column=2, sticky="ns")

        self.lbFilesList.config(yscrollcommand=self.scrollbar.set)


        btShowOriginal = ttk.Button(self.files_frame, text="Show Original", width=20, command=self.show_org)
        btShowOriginal.grid(row=2, column=0, padx=5, pady=5)

        btShowDuplicate = ttk.Button(self.files_frame, text="Show Duplicate", width=20, command=self.show_dup)
        btShowDuplicate.grid(row=2, column=1, padx=5)

        btOpenFolderOrg = ttk.Button(self.files_frame, text="Show Original Location", width=20, command=self.open_org_folder)
        btOpenFolderOrg.grid(row=3, column=0, padx=5, pady=5)

        btOpenFolderDup = ttk.Button(self.files_frame, text="Show Duplicate Location", width=20, command=self.open_dup_folder)
        btOpenFolderDup.grid(row=3, column=1, padx=5)

        btRmOrg = ttk.Button(self.files_frame, text="Remove Original", width=20, command=self.delete_org)
        btRmOrg.grid(row=4, column=0, padx=5, pady=5)

        btRmDup = ttk.Button(self.files_frame, text="Remove Duplicate", width=20, command=self.delete_dup)
        btRmDup.grid(row=4, column=1, padx=5)

        btNotDuplicateOrg = ttk.Button(self.files_frame, text="This is not duplicate", width=20, command=self.not_duplicate_org)
        btNotDuplicateOrg.grid(row=5, column=0, padx=5)

        btNotDuplicateDup = ttk.Button(self.files_frame, text="This is not duplicate", width=20, command=self.not_duplicate_dup)
        btNotDuplicateDup.grid(row=5, column=1, padx=5)

        lbPictypeOrg = ttk.Label(self.files_frame, text="Original:", font="default 10 bold")
        lbPictypeOrg.grid(row=0, column=3)
        lbPictypeDup = ttk.Label(self.files_frame, text="Duplicate:", font="default 10 bold")
        lbPictypeDup.grid(row=0, column=4)

        self.lbProgress = ttk.Label(self.files_frame, text="Searching Progress:", font="default 10 bold")
        self.lbProgress.grid(row=4, column=3, sticky="sw")
        self.progress_bar = ttk.Progressbar(self.files_frame, orient="horizontal", length=450, mode="determinate", takefocus=True)#, maximum=100)
        self.progress_bar.grid(row=5, column=3, columnspan=2) 

        self.nopicpath = "nopic.jpg"
        self.no_preview_pic = "nopreview.png"

        file1 = self.nopicpath
        file2 = self.nopicpath

# loading default picture
        self.img1 = Image.open(file1).resize((200, 200))
        self.img2 = Image.open(file2).resize((200, 200))
        self.pic1 = ImageTk.PhotoImage(self.img1)
        self.pic2 = ImageTk.PhotoImage(self.img2)
        self.lbDisplayImg1 = Label(self.files_frame, image=self.pic1)
        self.lbDisplayImg1.grid(row=1, column=3, rowspan=2, pady=2, padx=5)
        self.lbDisplayImg2 = Label(self.files_frame, image=self.pic2)
        self.lbDisplayImg2.grid(row=1, column=4, rowspan=2, pady=2)

        self.details_frame = ttk.Frame(master)
        self.details_frame.pack()

        lbFilesDetails = ttk.Label(self.details_frame, text="Files Details", font="default 10 bold")
        lbFilesDetails.grid(row=0, column=0)

        
        self.txtDetails = Text(self.details_frame, bg="#99A799", font=("default", 10), width=104)
        self.txtDetails.insert(0.0, f"Files is not selected.")
        self.txtDetails.config(state=DISABLED)
        self.txtDetails.grid(row=2, column=0)


# selecting a folder to scan and inserting path to Directory entry box
    def count_dups(self, duplicates):
        return len(duplicates.keys())

    def select_folder(self):
        path = tkinter.filedialog.askdirectory()
        self.enDirectory.delete(0, "end")
        self.enDirectory.insert(0, path)

    def scan(self):
        self.lbFilesList.delete(0,'end')
        self.progress_bar["value"] = 0

# selecting right OS in order to make sure selected folder path is correct
        if self.var.get() == 0 and platform.system()=="Windows":
            messagebox.showinfo("Info", "Incorrect operating system selected.")
            quit()
        elif self.var.get() ==1 and platform.system()=="Linux":
            messagebox.showinfo("Info", "Incorrect operating system selected.")
            quit()
        elif self.var.get() == 0:
            self.selected_folder = self.enDirectory.get() + "//" #for linux paths
        elif self.var.get() == 1:
            self.selected_folder = self.enDirectory.get() + "\\" #for windows

# initializing collections for gathering orgiginal and duplicate files
        self.all_originals={}
        self.duplicate_list = []
        self.filelist = []


# creates a list with all files from main and all subdirectories
        # self.selected_folder = "/home/adam/Desktop/Python/FileDuplicatesFinder/TestFiles" #test folder
        for root, dirs, files in os.walk(self.selected_folder):
            for file in files:
                self.filelist.append(os.path.join(root, file))
        self.progress_len = len(self.filelist)

# going through the file list in order to find duplicates (also collecting the file paths, file names and file extensions for further processing)       
# takes each file in the list and then goes through all other files to match duplicated name 
        for name in enumerate(self.filelist):

# updating progress bar
            self.progress_bar["value"] += 100/self.progress_len
            self.select_frame.update()

            # getting file details (full name, file name and file extension) of each item
            full_file_path = name[1].rsplit(sep="\\", maxsplit=-1)[-1]#used as a key in final dictionary
            self.file_name = full_file_path.rsplit(sep="/", maxsplit=-2)[-1].split(".")[0]#used for file matching
            self.file_ext = full_file_path.rsplit(sep=".", maxsplit=-1)[-1] #used once
            self.file_name_ext = full_file_path.rsplit(sep="/", maxsplit=-2)[-1] #used as a key in final dictionary
# loop for the rest of files
            for duplicate in enumerate(self.filelist):
                full_duplicate_path = duplicate[1].rsplit(sep="\\", maxsplit=-1)[-1]
                self.duplicate_name = full_duplicate_path.rsplit(sep="/", maxsplit=-2)[-1].split(".")[0]
                self.duplicate_ext = full_duplicate_path.rsplit(sep=".", maxsplit=-1)[-1]
                self.duplicate_name_ext = full_duplicate_path.rsplit(sep="/", maxsplit=-2)[-1]
                file_copy_wildcard_1 = self.file_name + " (*)"
                file_copy_wildcard_2 = self.file_name + "(*)"
                duplicate_copy_wildcard_1 = self.duplicate_name + " (*)"
                duplicate_copy_wildcard_2 = self.duplicate_name + "(*)"
# conditions for the files that should not be included in final dictionary
                if name[0] == duplicate[0] or self.file_name in self.duplicate_list or self.duplicate_name in self.duplicate_list:
                    continue
                else:
# conditions that indiciate that file has a duplicate                    
                    if (self.file_name == self.duplicate_name or 
                        fnmatch.fnmatch(self.duplicate_name, file_copy_wildcard_1) or 
                        fnmatch.fnmatch(self.file_name, duplicate_copy_wildcard_1) or
                        fnmatch.fnmatch(self.duplicate_name, file_copy_wildcard_2) or 
                        fnmatch.fnmatch(self.file_name, duplicate_copy_wildcard_2)):
                        self.all_originals[self.file_name_ext]=(full_file_path, full_duplicate_path)
                        self.duplicate_list.append(self.duplicate_name)

        self.lbFiles.configure(text=f"Files and duplicates({self.count_dups(self.all_originals)}):")
        if self.all_originals == {}:
            messagebox.showinfo("Info", "No duplicated files found.")

#filling listbox
        for item in self.all_originals: 
            self.lbFilesList.insert(list(self.all_originals.keys()).index(item), item)
        self.lbFilesList.bind("<<ListboxSelect>>", self.lb_duplicates)
        self.lbFilesList.grid(row=1, column=0, columnspan=2)
        self.scrollbar.config(command = self.lbFilesList.yview)


    def lb_duplicates(self, event): 

# variables for listbox selection (orginal and duplicate file)
        self.org_file = self.all_originals[self.lbFilesList.get((self.lbFilesList.curselection()))][0]
        self.dup_file = self.all_originals[self.lbFilesList.get((self.lbFilesList.curselection()))][1]

        # HANDLING FILE TYPES
        self.org_file_type = magic.from_file(self.org_file, mime=True).split("/")[0] 
        self.dup_file_type = magic.from_file(self.dup_file, mime=True).split("/")[0] 

# -------------------------ORIGINALS----------------------------
# showing picture samples    
        try:
            # video thumbnail show

            if self.is_video(self.org_file_type):
                cap = cv2.VideoCapture(self.org_file)
                cap.set(1,0.1) 
                ret, frame = cap.read()
                org_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.org_pic=Image.fromarray(org_RGB)
# HEIC format handilng
            elif self.org_file.rsplit(sep='.', maxsplit=-1)[-1] == "HEIC":
                try:
                    heif_file = pyheif.read(self.org_file)
                    self.org_pic = Image.frombytes(
                        heif_file.mode, 
                        heif_file.size, 
                        heif_file.data,
                        "raw",
                        heif_file.mode,
                        heif_file.stride,
                        )
                except ValueError:
                    messagebox.showerror("Error", "File is corrupted. Not a HEIC file!")
            else:
                self.org_pic1 = Image.open(self.org_file)
                self.org_pic = self.rotation(self.org_pic1)#rotation of the pictures (some of picture samples were automatically rotated )
        except:
# in case file is non-picture loads a default pic
            self.org_pic = Image.open(self.no_preview_pic)

        org_pic_resized = self.org_pic.resize((200, 200))

# -------------------------DUPLICATES----------------------------
# showing picture samples   
        try:
            if self.is_video(self.dup_file_type):
                file_is_video = True
                cap = cv2.VideoCapture(self.dup_file)
                cap.set(1,0.1)
                ret, frame = cap.read()
                dup_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.dup_pic=Image.fromarray(dup_RGB)
                end = time.time()
    # HEIC format handilng
            elif self.dup_file.rsplit(sep='.', maxsplit=-1)[-1] == "HEIC":
                try:
                    heif_file = pyheif.read(self.dup_file)
                    self.dup_pic = Image.frombytes(
                        heif_file.mode, 
                        heif_file.size, 
                        heif_file.data,
                        "raw",
                        heif_file.mode,
                        heif_file.stride,
                        )
                except ValueError:
                    messagebox.showerror("Error", "File is corrupted. Not a HEIC file!")
            else:
    # regular formats handling
                self.dup_pic1 = Image.open(self.dup_file)
                self.dup_pic = self.rotation(self.dup_pic1)#rotation of the pictures (some of picture samples were automatically rotated )
        except:
# # in case file is non-picture loads a default pic
            self.dup_pic = Image.open(self.no_preview_pic)

        dup_pic_resized = self.dup_pic.resize((200, 200))

        self.org_pic_sample = ImageTk.PhotoImage(org_pic_resized)
        self.lbDisplayImg1.configure(image=self.org_pic_sample)

        self.dup_pic_sample = ImageTk.PhotoImage(dup_pic_resized)
        self.lbDisplayImg2.configure(image=self.dup_pic_sample)

# showing pic details
        org_size = os.stat(self.org_file)
        dup_size = os.stat(self.dup_file)
        org_time_date = time.ctime(os.path.getctime(self.org_file))
        dup_time_date = time.ctime(os.path.getctime(self.dup_file))

        self.txtDetails.config(state="normal")
        self.txtDetails.delete(0.0, END)
        self.txtDetails.insert(0.0, f"""File name: {self.lbFilesList.get((self.lbFilesList.curselection()))}\n
            \nOriginal File:
            \nPath: {self.org_file}
            \nSize: {org_size.st_size/1000000} MB
            \nLength: {self.video_length(self.org_file) if self.is_video(self.org_file_type) else "---"}
            \nResolution: {str(self.org_pic.size[0]) + "x" + str(self.org_pic.size[1]) if self.is_picture(self.org_file_type) or self.is_video(self.org_file_type) else "---"}
            \n-----------------------------------------------------
            \nDuplicate File:
            \nPath: {self.dup_file}
            \nSize: {dup_size.st_size/1000000} MB 
            \nLength: {self.video_length(self.dup_file) if self.is_video(self.dup_file_type) else "---"}
            \nResolution: {str(self.dup_pic.size[0]) + "x" + str(self.dup_pic.size[1]) if self.is_picture(self.dup_file_type) or self.is_video(self.dup_file_type) else "---"}
            """)
# CHANGE CREATION DATE TO LENGTH IN CASE OF MOVIE AND CHANGE RESOLUTION IN CASE OF NON PIC FILES
        self.txtDetails.config(state="disabled")


    def is_video(self, file):
        if file == "video":
            return True

    def is_picture(self, file):
        if file == "image":
            return True

    def video_length(self, file):
        video = cv2.VideoCapture(file)
        frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = int(video.get(cv2.CAP_PROP_FPS))
        seconds = int(frames/fps)
        video_length = str(datetime.timedelta(seconds=seconds))
        return video_length


# function to rotate misoriented pictures
    def rotation(self, pil_img):
        img_exif = pil_img.getexif()
        try:
            if len(img_exif):
                if img_exif[274] == 3:
                    pil_img = pil_img.transpose(Image.ROTATE_180)
                elif img_exif[274] == 6:
                    pil_img = pil_img.transpose(Image.ROTATE_270)
                elif img_exif[274] == 8:
                    pil_img = pil_img.transpose(Image.ROTATE_90)
        except KeyError:
            pass
        return pil_img

# removing original file (+ item from listbox, info from File Details)
    def delete_org(self):
        try:
            os.remove(self.org_file)
            index_curselection = self.lbFilesList.curselection()
            self.lbFilesList.delete(self.lbFilesList.curselection())
            self.next_item(index_curselection)
        except tkinter.TclError:
            messagebox.showerror("Error!", "No file selected!")

        self.txtDetails.config(state="normal")
        self.txtDetails.delete(0.0, END)
        self.txtDetails.insert(0.0, f"Files is not selected.")
        self.txtDetails.config(state="disabled")
        

        self.preview = Image.open(self.no_preview_pic)
        self.preview_resized = self.preview.resize((200, 200))
        self.open_preview1 = ImageTk.PhotoImage(self.preview_resized)
        self.lbDisplayImg1.configure(image=self.open_preview1)
        
        self.preview = Image.open(self.no_preview_pic)
        self.preview_resized = self.preview.resize((200, 200))
        self.open_preview2 = ImageTk.PhotoImage(self.preview_resized)
        self.lbDisplayImg2.configure(image=self.open_preview2)

# removing duplicate file (+ item from listbox, info from File Details)
    def delete_dup(self):
        try:
            os.remove(self.dup_file)
            index_curselection = self.lbFilesList.curselection()
            self.lbFilesList.delete(self.lbFilesList.curselection())
            self.next_item(index_curselection)
        except tkinter.TclError:
            messagebox.showerror("Error!", "No file selected!")

        self.txtDetails.config(state="normal")
        self.txtDetails.delete(0.0, END)
        self.txtDetails.insert(0.0, f"Files is not selected.")
        self.txtDetails.config(state="disabled")

        self.preview = Image.open(self.no_preview_pic)
        self.preview_resized = self.preview.resize((200, 200))
        self.open_preview1 = ImageTk.PhotoImage(self.preview_resized)
        self.lbDisplayImg1.configure(image=self.open_preview1)
        
        self.preview = Image.open(self.no_preview_pic)
        self.preview_resized = self.preview.resize((200, 200))
        self.open_preview2 = ImageTk.PhotoImage(self.preview_resized)
        self.lbDisplayImg2.configure(image=self.open_preview2)

# opening original picture in system default picture browser
    def show_org(self):
        try:
            if self.is_picture(self.org_file_type): #HOW TO OPEN VIDEO FILE??
                self.org_pic.show()
            elif self.is_video(self.org_file_type):
                self.play_video(self.org_file)
        except tkinter.TclError:
            messagebox.showerror("Error!", "No file selected!")

# opening duplicate picture in system default picture browser
    def show_dup(self):
        try:
            if self.is_picture(self.dup_file_type): 
                self.org_pic.show()
            elif self.is_video(self.dup_file_type):
                self.play_video(self.dup_file)
        except tkinter.TclError:
            messagebox.showerror("Error!", "No file selected!")

# opening video file 
    def play_video(self, file):
        cap = cv2.VideoCapture(file)
        dim = (800, 800)
        font = cv2.FONT_HERSHEY_SIMPLEX
        while(cap.isOpened()):  
          ret, frame = cap.read()
          frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
          if ret == True:
            cv2.putText(frame, "Press Esc to exit", (50, 100), font, 2, (0,0,0),3 )
            cv2.imshow('Frame', frame)
            if cv2.waitKey(25) & 0xFF == ord('\x1b'):
              break
          else: 
            break
        cap.release()
        cv2.destroyAllWindows()
        # new window after closing the video, how to prevent that??????

# opening a folder where original picture is
    def open_org_folder(self):
        try:
            org_path = self.org_file
            folder_path = "/".join(org_path.split("/")[0:-1])
            subprocess.Popen(['xdg-open', folder_path])
        except tkinter.TclError:
            messagebox.showerror("Error!", "No file selected!")

# opening a folder where duplicate picture is
    def open_dup_folder(self):
        try:
            org_path = self.dup_file
            folder_path = "/".join(org_path.split("/")[0:-1])
            subprocess.Popen(['xdg-open', folder_path])
        except tkinter.TclError:
            messagebox.showerror("Error!", "No file selected!")

#renaming original file in case files are not the same (and removing file from listbox + file details)
    def not_duplicate_org(self):
        try:
            self.txtDetails.config(state="normal")
            self.txtDetails.delete(0.0, END)
            self.txtDetails.insert(0.0, f"Files is not selected.")
            self.txtDetails.config(state="disabled")

            self.preview = Image.open(self.no_preview_pic)
            self.preview_resized = self.preview.resize((200, 200))
            self.open_preview1 = ImageTk.PhotoImage(self.preview_resized)
            self.lbDisplayImg1.configure(image=self.open_preview1)
            
            self.preview = Image.open(self.no_preview_pic)
            self.preview_resized = self.preview.resize((200, 200))
            self.open_preview2 = ImageTk.PhotoImage(self.preview_resized)
            self.lbDisplayImg2.configure(image=self.open_preview2)
        
            os.rename(self.dup_file, 
                (self.dup_file.split(".")[0])
                + "_unique." + self.dup_file.rsplit(sep=".", maxsplit=-1)[-1])

            index_curselection = self.lbFilesList.curselection()
            self.lbFilesList.delete(self.lbFilesList.curselection())
            self.next_item(index_curselection)

        except tkinter.TclError:
            messagebox.showerror("Error!", "No file selected!")

#renaming duplicate file in case files are not the same (and removing file from listbox + file details)
    def not_duplicate_dup(self):

        try:
            self.txtDetails.config(state="normal")
            self.txtDetails.delete(0.0, END)
            self.txtDetails.insert(0.0, f"Files is not selected.")
            self.txtDetails.config(state="disabled")

            self.preview = Image.open(self.no_preview_pic)
            self.preview_resized = self.preview.resize((200, 200))
            self.open_preview1 = ImageTk.PhotoImage(self.preview_resized)
            self.lbDisplayImg1.configure(image=self.open_preview1)
            
            self.preview = Image.open(self.no_preview_pic)
            self.preview_resized = self.preview.resize((200, 200))
            self.open_preview2 = ImageTk.PhotoImage(self.preview_resized)
            self.lbDisplayImg2.configure(image=self.open_preview2)
        
            os.rename(self.dup_file, 
                (self.dup_file.split(".")[0])
                + "_unique." + self.dup_file.rsplit(sep=".", maxsplit=-1)[-1])

            index_curselection = self.lbFilesList.curselection()
            self.lbFilesList.delete(self.lbFilesList.curselection())
            self.next_item(index_curselection)

        except tkinter.TclError:
            messagebox.showerror("Error!", "No file selected!")

            # AFTER RE-SCANNING THE COUNT RESOULT IS INACCURATE1 PUT THE PROGRESS BAR TO NEW WINDOW SO I KNOW THE PROCESS STARTED TO RUN??

# how to display next item on the list??
    def next_item(self, index):
        print(index[0])
        
        self.lbFilesList.select_set(index[0])
        




def main():
    root = Tk()
    duplicates = Duplicates(root)
    root.mainloop()


if __name__ == '__main__':
    main()