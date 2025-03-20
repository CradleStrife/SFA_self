// src/vue.d.ts
import { ComponentCustomProperties } from 'vue';

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $apiHost: string;
  }
}
