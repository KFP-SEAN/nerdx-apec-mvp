/**
 * Type definitions for @google/model-viewer web component
 */

declare namespace JSX {
  interface IntrinsicElements {
    'model-viewer': ModelViewerJSX & React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
  }
}

interface ModelViewerJSX {
  src?: string;
  alt?: string;
  ar?: boolean;
  'ar-modes'?: string;
  'ar-scale'?: string;
  'camera-controls'?: boolean;
  'camera-orbit'?: string;
  'camera-target'?: string;
  'environment-image'?: string;
  exposure?: string;
  'field-of-view'?: string;
  'max-camera-orbit'?: string;
  'min-camera-orbit'?: string;
  'max-field-of-view'?: string;
  'min-field-of-view'?: string;
  'interaction-prompt'?: string;
  'interaction-prompt-style'?: string;
  'interaction-prompt-threshold'?: string;
  'auto-rotate'?: boolean;
  'auto-rotate-delay'?: string;
  'rotation-per-second'?: string;
  'shadow-intensity'?: string;
  'shadow-softness'?: string;
  poster?: string;
  reveal?: string;
  loading?: string;
  'quick-look-browsers'?: string;
  'touch-action'?: string;
  'disable-zoom'?: boolean;
  'disable-pan'?: boolean;
  'disable-tap'?: boolean;
  bounds?: string;
  interpolation-decay?: string;

  // Event handlers
  onLoad?: (event: Event) => void;
  onError?: (event: ErrorEvent) => void;
  'onAr-activate'?: (event: Event) => void;

  // React props
  ref?: React.Ref<any>;
  style?: React.CSSProperties;
  className?: string;
  children?: React.ReactNode;
}
