import { Component } from '@angular/core';
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
export class ChatInterface {
  messages: any[] = [];
  userInput: string = '';
  level: string = 'A1';
  score: number = 0;
  isRecording = false;
  mediaRecorder: any;
  audioChunks: any[] = [];

  constructor(private coachService: CoachService) {}

  sendMessage() {
    if (!this.userInput.trim()) return;

    const userMsg = { role: 'user', content: this.userInput };
    this.messages.push(userMsg);
    
    const textToSend = this.userInput;
    this.userInput = ''; 

    this.coachService.chat(textToSend, this.messages, this.level).subscribe({
      next: (res: any) => {
        const coachMsg = { role: 'assistant', content: res.response };
        this.messages.push(coachMsg);
        this.playResponse(res.response);
        
        if (res.response.includes('10/10')) {
          this.score += 2;
        }
      },
      error: (err) => {
        console.error('Connexion au serveur Python échouée', err);
        this.messages.push({ 
          role: 'assistant', 
          content: 'Sorry, I am having trouble connecting to my brain. Is FastAPI running?' 
        });
      }
    });
  }

  async startRecording() {
    try {
      this.isRecording = true;
      this.audioChunks = [];
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);

      this.mediaRecorder.ondataavailable = (event: any) => {
        this.audioChunks.push(event.data);
      };

      this.mediaRecorder.onstop = () => {
        // On crée le blob à partir des données collectées
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });

        // CRUCIAL : On emballe le blob dans un FormData
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        // On envoie le formData (et non le blob seul)
        this.coachService.sendAudio(formData).subscribe({
          next: (res: any) => {
            console.log('Transcription réussie :', res.text);
            this.userInput = res.text;
            this.sendMessage(); 
          },
          error: (err) => {
            console.error('Erreur STT complète :', err);
            this.isRecording = false;
          }
        });
      };
      this.mediaRecorder.onstop = () => {
      const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');

      this.coachService.sendAudio(formData).subscribe({
        next: (res: any) => {
          // Si l'IA a compris quelque chose
          if (res.text && res.text.trim().length > 0) {
            console.log('Texte capté :', res.text);
            this.userInput = res.text; // On remplit le champ
            this.sendMessage();        // On l'envoie dans le chat
          } else {
            // Optionnel : afficher un petit message si le micro n'a rien capté
            console.warn("L'audio semble vide ou incompréhensible.");
          }
        },
        error: (err) => {
          console.error('Erreur STT complète :', err);
          this.isRecording = false;
        }
      });
    };

      this.mediaRecorder.start();
    } catch (err) {
      console.error('Microphone inaccessible', err);
      this.isRecording = false;
    }
  }

  stopRecording() {
    if (this.mediaRecorder && this.isRecording) {
      this.isRecording = false;
      this.mediaRecorder.stop();
    }
  }

  playResponse(text: string) {
    const audioUrl = this.coachService.getVoiceUrl(text);
    const audio = new Audio(audioUrl);
    audio.play().catch(e => console.warn("Audio play blocked or failed", e));
  }
}