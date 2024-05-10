

class ResultSubtitlesParser:
    @staticmethod
    def seconds_to_timestamp(secondsStr:float) -> str:
        secondsStr= str(secondsStr)
        seconds= float(secondsStr.split(".")[0])
        milliseconds= secondsStr.split(".")[1]

        hours, minutes = divmod(seconds, 3600)
        minutes, seconds = divmod(minutes, 60)
        
        time_vals= [str(int(hours)),str(int(minutes)),str(int(seconds))]

        for idx, value in enumerate(time_vals):
            if len(value) == 1:
                time_vals[idx] = "0" + value
        return(time_vals[0]+":"+time_vals[1]+":"+time_vals[2]+","+str(milliseconds).ljust(3,"0"))
    
    @classmethod
    def parse_output(self, transcriptDict: dict) -> str:
        transcript= ""
        for idx, segment in enumerate(transcriptDict["segments"]):
            start_seconds= segment["start"]
            end_seconds= segment["end"]
            text= segment["text"]
            transcript += str(idx + 1) + "\n" + self.seconds_to_timestamp(start_seconds) + " --> " + self.seconds_to_timestamp(end_seconds) + "\n" + text + "\n\n"

        return(transcript)

    @classmethod
    def parse_output_diarized(self, transcriptDictDiarized: dict) -> str:
        transcript= ""
        for idx, segment in enumerate(transcriptDictDiarized["segments"]):
            print(segment)
            start_seconds= segment["start"]
            end_seconds= segment["end"]
            speaker= segment["speaker"] if "speaker" in segment else "Unknown"
            text= segment["text"]
            transcript += str(idx + 1) + "\n" + self.seconds_to_timestamp(start_seconds) + " --> " + self.seconds_to_timestamp(end_seconds) + "\n" + f"{speaker}: " + text + "\n\n"

        return(transcript)