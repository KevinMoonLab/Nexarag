import { Component, ViewEncapsulation, computed, inject, model } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DropdownModule } from 'primeng/dropdown';
import { ButtonModule } from 'primeng/button';
import { DividerModule } from 'primeng/divider';
import { TabsModule } from 'primeng/tabs';
import { ChatService } from './chat.service';

@Component({
  selector: 'app-chat-settings',
  standalone: true,
  imports: [CommonModule, FormsModule, DropdownModule, ButtonModule, DividerModule, TabsModule],
  template: `
    <div class="p-4 w-full space-y-4">
      <div>
        <label for="modelDropdown" class="block mb-2 font-medium">Select Model</label>
        <p-dropdown 
          inputId="modelDropdown"
          [options]="availableModels()" 
          [(ngModel)]="chatService.selectedModel"
          optionLabel="label"
          optionValue="value"
          placeholder="Choose a model"
          class="w-full"
        ></p-dropdown>  
      </div>

      <div>
        <label for="promptTextarea" class="block mb-2 font-medium">Default Prompt</label>
        <textarea
          pInputTextarea
          id="promptTextarea"
          [(ngModel)]="prompt"
          rows="4"
          class="w-full text-black p-2 border rounded-lg"
          placeholder="Enter a default prompt..."
        ></textarea>
      </div>
    </div>
  `,
  styles: [],
  encapsulation: ViewEncapsulation.None,
})
export class ChatSettingsComponent {
  chatService = inject(ChatService);

  availableModels = computed(() => {
    const models = this.chatService.models();
    console.log(models);
    const options = models.map(model => ({
      label: model.model,
      value: model.model,
    }));
    return options;
  });

  prompt = model('');
}