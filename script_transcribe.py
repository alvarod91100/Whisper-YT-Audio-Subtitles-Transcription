import os
import torch
import whisperx
from typing import Tuple
from utils.misc import showFiles, showDir
from utils.ResultSubtitlesParser import ResultSubtitlesParser
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()

MAX_SPEAKERS = 2
MIN_SPEAKERS = 1
AUDIO_DIR = "audio/"
MODELS_DIR = "/mnt/c/Users/alvar/Documents/DeepLearning-Models/Whisper/models_whisper"
HUGGINGFACE_KEY = os.getenv('HUGGINGFACE_KEY')
WHISPER_MODEL = os.getenv('WHISPER_MODEL') if os.getenv('WHISPER_MODEL') else  "distil-large-v2"
BATCH_SIZE= os.getenv('BATCH_SIZE') if os.getenv('BATCH_SIZE') else 16
CHUNK_SIZE= os.getenv('CHUNK_SIZE') if os.getenv('CHUNK_SIZE') else 8

def checkCUDA() -> str:
    available_gpu_memory = round(torch.cuda.mem_get_info()[0]/1e9, 2) if torch.cuda.is_available() else 0
    compute_type, device = ("float16", "cuda") if available_gpu_memory >= 4 else ("float32", "cpu")
    print(f"Available GPU memory: {available_gpu_memory}GB")
    print(f"Using {device} with {compute_type} compute")
    return device, compute_type

def transcriptAudio(audioFilePath:str, device:str, compute_type:str) -> dict:
    model = whisperx.load_model(WHISPER_MODEL, device= device, compute_type=compute_type, download_root=MODELS_DIR)
    audio= whisperx.load_audio(audioFilePath)
    resultTranscription = model.transcribe(audio, batch_size=BATCH_SIZE, chunk_size=CHUNK_SIZE, print_progress=True)
    return resultTranscription, audio

def alignTranscription(resultTranscription, audio):
    model_a, metadata = whisperx.load_align_model(language_code=resultTranscription["language"], device=device,model_dir=MODELS_DIR)
    resultTranscriptionAligned = whisperx.align(resultTranscription["segments"], model_a, metadata, audio, device, return_char_alignments=False)
    del model_a
    return resultTranscriptionAligned

def diarizeTranscription(resultTranscriptionAligned, audio, min_speakers:int=1, max_speakers:int=2):
    diarize_model = whisperx.DiarizationPipeline(use_auth_token=HUGGINGFACE_KEY, device=device)
    diarize_segments = diarize_model(audio,min_speakers=min_speakers, max_speakers=max_speakers)
    resultTranscriptionDiarized = whisperx.assign_word_speakers(diarize_segments, resultTranscriptionAligned)
    del diarize_model, diarize_segments
    return resultTranscriptionDiarized

def diarizationPipeline(audioFilePath:str, device:str, compute_type:str, min_speakers:int=1, max_speakers:int=2):
    resultTranscription, audio = transcriptAudio(audioFilePath, device, compute_type)
    resultTranscriptionAligned = alignTranscription(resultTranscription, audio)
    resultTranscriptionDiarized = diarizeTranscription(resultTranscriptionAligned, audio, min_speakers=min_speakers, max_speakers=max_speakers)
    del resultTranscriptionAligned, resultTranscription
    return resultTranscriptionDiarized, audio

def parseAudio(resultDict:dict, fileName:str, diarize:bool = False) -> None:
    resultPath= "outputs/diarized/" if diarize else "outputs/transcripts/"
    parser = ResultSubtitlesParser()
    transcript= ResultSubtitlesParser.parse_output_diarized(resultDict) if diarize else ResultSubtitlesParser.parse_output(resultDict)
    with open(f"{resultPath}/{fileName.split('.')[0]}.srt", "w") as file:
        file.write(transcript)
        file.close()
    
def deleteVars() -> None:
    del model
    del audio
    del result

def filterAlreadyTranscribed(audioFilesPresent:list[str], transcriptsPath:str):
    transcriptFiles = [file.split(".")[0] for file in os.listdir(transcriptsPath)]
    common = [file for file in audioFilesPresent if file.split(".")[0] in transcriptFiles]
    print(len(common))
    if len(common) > 0:
        print(f"\nFound transcripts already processed for {len(common)} audios:")
    for item in common:
        print(f"\t- {item}")
    print("\n")
    #return list(files.difference(filesPresent).union(filesPresent.difference(files)))
    return [file for file in audioFilesPresent if file.split(".")[0] not in transcriptFiles]

def delete_all_variables():
    for name in dir():
        if not name.startswith('_'):
            del globals()[name]

if __name__ == "__main__":
    device, compute_type= checkCUDA()
    audioPath= showDir(AUDIO_DIR) + "/"
    files= showFiles(audioPath, "audio")
    audioChoice = int(input("Enter the file number you want to transcribe: "))
    methodChoice = int(input("\nWould you like to just get\n1) The normal subtitle transcript\nor\n2) The diarized transcript\nEnter your choice as number: "))
    resultPath =  "outputs/transcripts/" if methodChoice == 1 else "outputs/diarized/"
    filesProcess = files.values() if audioChoice  == -1 else [files[audioChoice]]
    filesProcess = filterAlreadyTranscribed(filesProcess, resultPath)
    print(f"Processing {len(filesProcess)} files: ")
    for fileName in tqdm(filesProcess):
        audioFilePath= audioPath + fileName
        print(f"Processing audio: {audioFilePath}", end= "\r")
        try:
            resultTranscription, _ = transcriptAudio(audioFilePath, device, compute_type) if methodChoice == 1 else diarizationPipeline(audioFilePath, device, compute_type, MIN_SPEAKERS, MAX_SPEAKERS)
        except Exception as e:
            print(f"Changing to float32 due to error: {e}")
            resultTranscription, _ = transcriptAudio(audioFilePath, device, compute_type) if methodChoice == 1 else diarizationPipeline(audioFilePath, device, compute_type, MIN_SPEAKERS, MAX_SPEAKERS)
        parsedAudio= parseAudio(resultTranscription, fileName, diarize= False if methodChoice == 1 else True)
        delete_all_variables()