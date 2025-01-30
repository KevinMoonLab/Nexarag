import { Component, input } from '@angular/core';

@Component({
  selector: 'app-node-card',
  template: `
    <div class="w-full bg-white rounded-lg p-4 space-y-2">
        <!-- Header -->
        <div class="text-xs font-medium text-gray-500">
            {{ header() }}
        </div>

        <!-- Body -->
        <div class="text-gray-800">
            {{ body() ?? '' }}
        </div>
    </div>
  `,
})
export class NodeCardComponent {
  header = input('');
  body = input('' as string|number|Date|undefined);
}