import whisper
import time
import datetime 
import os 
import math 

class Whisperos:
            
    def __init__(self):
        self.model_type = 'small' # tiny, base, small, medium, large, turbo

        self.folders_names = ["input", "transcript_output", "temp"]
        
        self.input_dir_path = self.return_path(self.folders_names[0])
        self.output_dir_path = self.return_path(self.folders_names[1]) 
        self.temp_cut_audio_dir_path = self.return_path(self.folders_names[2])
        
        self.setup_environment(self.folders_names)
        self.input_files_names = self.check_input_files_names()
        
        self.all_transcript = ""
        self.all_segments = ""

        self.transcription_time = ""
        self.load_model_time = ""
        
    def return_path(self, folder_name):
        return os.path.join(os.path.dirname(__file__),folder_name)
    
    def setup_environment(self, dir_names):
        for dir_name in dir_names:
            if not os.path.exists(dir_name):
                os.mkdir(dir_name) 
                print(f"Directory '{dir_name}' is created!")
          
            
    def check_input_files_names(self):
        res = []
        for file_path in os.listdir(self.input_dir_path):
            # check if current file_path is a file
            if os.path.isfile(os.path.join(self.input_dir_path, file_path)):
                # add filename to list
                res.append(file_path)
        if len(res) == 0:
            print(f"Copy audio files to input folder and run program again")
        else: 
            print("Input files: ",end="")
            print(res)
        return res            
    
    def split_audio(self, input_file, duration):
        print(f"Start split audio in {duration}s parts")
        input_file_name =  input_file[:len(input_file)-4]
        file_path = os.path.join(self.input_dir_path, input_file)
        print("file_path",file_path)
        audio = AudioSegment.from_mp3(file_path)
        total_length = len(audio)
        num_parts = math.ceil(total_length / (duration * 1000))
        new_files_names = []
        start_time = time.time()
        for i in range(num_parts):
            start = i * duration * 1000
            end = (i + 1) * duration * 1000
            split_audio = audio[start:end] 
            new_file_name = f"{input_file_name}_part_{i+1}.mp3"           
            output_path = os.path.join(self.temp_cut_audio_dir_path, new_file_name)
            split_audio.export(output_path, format="mp3")
            new_files_names.append(new_file_name)
            print(f"Exported {output_path}")
        end = time.time()
        cutting_time = self.calculate_time(round((end - start_time),2))
        print(f"Cutting time of '{input_file}': "+cutting_time)
        return new_files_names
    
    def transcript(self, mp3_file_name, mp3_file_path):        
        start = time.time()
        model = whisper.load_model(self.model_type)
        self.load_model_time = str(round((time.time() - start),2))
        print("Load model time: "+ self.load_model_time  + "s")
        print("Starting transcripting...")
        start = time.time()
        result = model.transcribe(mp3_file_path, language="pl", fp16=False)
        end = time.time()
        transcription_time = self.calculate_time(round((end - start),2))
        self.transcription_time = transcription_time
        print(f"Transcription time of '{mp3_file_name}': "+transcription_time)
        self.save_transcript_to_variables(result)
        #self.save_transcript_to_file(mp3_file_name,transcription_time,result)
        
    def save_transcript_to_variables(self, result):
        self.all_transcript += result["text"]+"\n"
        for segment in result['segments']:
            self.all_segments += ("["+str(round(segment['start'],2)) + "-" + str(round(segment['end'],2))+"]"+segment['text']+"\n") 
        
    def save_transcript_to_file(self, file_name,work_time):
        oryginal_file_name = file_name
        file_name = file_name[:len(file_name)-4]+datetime.datetime.now().strftime("_%m-%d-%Y-%H:%M:%S")+"_ALL.txt" 
        transcript_file_save_path = os.path.join(self.output_dir_path,file_name)
        with open(transcript_file_save_path, 'w') as f:  
            f.write("File name: "+oryginal_file_name+"\n")  
            f.write("model type: "+self.model_type+"\n")                    
            f.write("loading model time: "+self.load_model_time+" s"+"\n")
            f.write("transcription time: "+self.transcription_time+"\n")   
            f.write("whole work time: "+work_time+"\n"+"\n")
            f.write(self.all_transcript+"\n"+"\n")
            
        with open(transcript_file_save_path, "a") as f:
            f.write(self.all_segments)
        print(f"File '{file_name}' is saved in '{self.output_dir_path}' directory \n")
        self.all_transcript = ""
        self.all_segments = ""
        print(f"Control status: self.all_transcript = '{self.all_transcript}' , self.all_segments= '{self.all_segments}' \n")
        
    def create_path_to_input_file(self,file_name):        
        return os.path.join(self.temp_cut_audio_dir_path, file_name)

    def create_path_to_input_file_only_imput(self,file_name):        
        return os.path.join(self.input_dir_path, file_name)
        
    def calculate_time(self, transcription_time):
        timedelta_obj = datetime.timedelta(seconds=int(transcription_time))
        return str(timedelta_obj)
        
    def delete_files_in_directory(self, directory_path ):
        for filename in os.listdir(directory_path):
            if os.path.isfile(os.path.join(directory_path, filename)):
                os.remove(os.path.join(directory_path, filename))
                
                
    def run(self):
        for input_file in self.input_files_names:
            start = time.time()
            print(f"------------------------{input_file}------------------------")
            
            # cut_files_names = self.split_audio(input_file,300)
            # for new_file_name in cut_files_names:
            #     print(f"\n------------------------Transcript: {new_file_name}")
            #     input_file_path = self.create_path_to_input_file(new_file_name)
            #     self.transcript(new_file_name,input_file_path)
            
            input_file_path = self.create_path_to_input_file_only_imput(input_file)
            self.transcript(input_file,input_file_path)
            end = time.time()
            work_time = self.calculate_time(round((end - start),2))
            self.save_transcript_to_file(input_file, work_time)
            self.delete_files_in_directory(self.temp_cut_audio_dir_path);
            
transcriptor = Whisperos()
transcriptor.run()



