import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { ShellComponent } from './shell.component';

@Component({
  imports: [ShellComponent, RouterModule],
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  title = 'Nexarag';
}
