import { Component, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CoachService } from '../../services/coach.service';

@Component({
  selector: 'app-chat-interface',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat-interface.html',
  styleUrls: ['./chat-interface.css']
})
export class ChatInterface implements AfterViewChecked {
  @ViewChild('scrollMe') private chatContainer!: ElementRef;
  messages: any[] = [];
  userInput: string = '';
  level: string = 'A1';
  score: number = 0;
  isRecording = false;
  mediaRecorder: MediaRecorder | null = null;
  audioChunks: Blob[] = [];

  constructor(private coachService: CoachService) {}
  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }
  private scrollToBottom(): void {
    try {
      // scroll instantané
      // this.chatContainer.nativeElement.scrollTop = this.chatContainer.nativeElement.scrollHeight;

      // scroll fluide
      this.chatContainer.nativeElement.scrollTo({ 
        top: this.chatContainer.nativeElement.scrollHeight, 
        behavior: 'smooth' 
      });
    } catch (err) {}
  }
sendMessage() {
  if (!this.userInput.trim()) return;

  // 1. Prepare the message for the UI
  const userMsg = { role: 'user', content: this.userInput };
  
  // 2. Capture history BEFORE pushing the new message
  // This prevents the AI from seeing your current message twice
  const historyToSend = [...this.messages]; 

  const textToSend = this.userInput;
  this.userInput = ''; 
  this.messages.push(userMsg); // Push to UI after capturing history

  this.coachService.chat(textToSend, historyToSend, this.level).subscribe({
    next: (res: any) => {
      // Update the level if the backend detected a new one
      if(res.detected_level) {
        this.level = res.detected_level;
      }

      const coachMsg = { role: 'assistant', content: res.response };
      this.messages.push(coachMsg);
      this.playResponse(res.response);
      
      if (res.response.includes('10/10')) {
        this.score += 2;
      }
    },
    error: (err) => {
      console.error('Connexion failed', err);
      this.messages.push({ 
        role: 'assistant', 
        content: 'Connection lost. Is the FastAPI server running?' 
      });
    }
  });
}

  async startRecording() {
    if (this.isRecording) return;
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.error('getUserMedia non supporté par le navigateur');
      this.messages.push({ role: 'assistant', content: "Votre navigateur n'autorise pas l'accès au microphone." });
      return;
    }

    try {
      this.isRecording = true;
      this.audioChunks = [];
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Choisir un mimeType supporté si possible
      let options: any = {};
      try {
        if ((window as any).MediaRecorder && (window as any).MediaRecorder.isTypeSupported) {
          if ((window as any).MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
            options = { mimeType: 'audio/webm;codecs=opus' };
          } else if ((window as any).MediaRecorder.isTypeSupported('audio/webm')) {
            options = { mimeType: 'audio/webm' };
          } else if ((window as any).MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
            options = { mimeType: 'audio/ogg;codecs=opus' };
          }
        }
      } catch (e) {
        console.warn('Erreur détection MIME MediaRecorder', e);
      }

      this.mediaRecorder = new MediaRecorder(stream, options);

      this.mediaRecorder.ondataavailable = (event: BlobEvent) => {
        if (event.data && event.data.size > 0) this.audioChunks.push(event.data);
      };

      this.mediaRecorder.onstop = async () => {
        const mime = options && options.mimeType ? options.mimeType : 'audio/webm';
        const audioBlob = new Blob(this.audioChunks, { type: mime });
        const filename = mime.includes('ogg') ? 'recording.ogg' : 'recording.webm';
        const formData = new FormData();
        formData.append('audio', audioBlob, filename);

        try {
          this.coachService.sendAudio(formData).subscribe({
            next: (res: any) => {
              if (res.text && res.text.trim().length > 0) {
                console.log('Texte capté :', res.text);
                this.userInput = res.text;
                this.sendMessage();
              } else {
                console.warn("L'audio semble vide ou incompréhensible.");
              }
            },
            error: (err) => {
              console.error('Erreur STT complète :', err);
              this.messages.push({ role: 'assistant', content: 'Erreur lors de la transcription audio.' });
            }
          });
        } finally {
          this.isRecording = false;
        }
      };

      this.mediaRecorder.start();
    } catch (err) {
      console.error('Microphone inaccessible', err);
      this.messages.push({ role: 'assistant', content: "Impossible d'accéder au micro. Vérifiez les permissions." });
      this.isRecording = false;
    }
}


  stopRecording() {
    if (this.mediaRecorder && this.isRecording) {
      try {
        this.mediaRecorder.stop();
      } catch (e) {
        console.warn('Erreur en stoppant MediaRecorder', e);
      } finally {
        this.isRecording = false;
      }
    }
}

  playResponse(text: string) {
    const audioUrl = this.coachService.getVoiceUrl(text);
    const audio = new Audio(audioUrl);
    audio.play().catch(e => console.warn("Audio play blocked or failed", e));
  }
}
