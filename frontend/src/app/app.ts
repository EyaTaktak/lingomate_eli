import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common'; // Import important
import { ChatInterface } from './components/chat-interface/chat-interface'; // Ton composant

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, ChatInterface],
  templateUrl: './app.html', // Retrait de ".component"
  styleUrl: './app.css'      // Retrait de ".component"
})
export class App{
  protected readonly title = signal('english-coach');
}
