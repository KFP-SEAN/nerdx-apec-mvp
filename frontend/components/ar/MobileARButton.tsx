/**
 * Mobile AR Quick Launch Button
 */

'use client';

import { useState } from 'react';

interface MobileARButtonProps {
  productHandle: string;
  arAssetUrl?: string;
}

export function MobileARButton({ productHandle, arAssetUrl }: MobileARButtonProps) {
  const [isSupported, setIsSupported] = useState(true);

  function launchAR() {
    if (arAssetUrl) {
      window.location.href = `/ar-viewer?product=${productHandle}&model=${encodeURIComponent(arAssetUrl)}`;
    }
  }

  if (!arAssetUrl) return null;

  return (
    <button
      onClick={launchAR}
      className="w-full mt-4 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition font-semibold shadow-lg"
    >
      🥽 AR로 미리보기
    </button>
  );
}
