import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment.prod';
@Injectable({ providedIn: 'root' })
export class CoachService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // Envoyer le texte au LLM
  chat(text: string, history: any[], level: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/chat`, { text, history, level });
  }

  // Modifié pour accepter le FormData envoyé par le composant
  sendAudio(data: FormData): Observable<any> {
    // Note : On ne définit PAS de headers ici, Angular s'en occupe
    return this.http.post(`${this.apiUrl}/stt`, data);
  }

  // Récupérer l'URL de la voix pour gTTS
  getVoiceUrl(text: string): string {
    return `${this.apiUrl}/tts?text=${encodeURIComponent(text)}`;
  }
}