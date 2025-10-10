/**
 * AR Viewer Page
 *
 * Displays AR experience for purchased products
 * Uses WebXR and model-viewer for AR visualization
 */

'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Cube, Download, RotateCw, Maximize2, Info, AlertCircle } from 'lucide-react';
import Script from 'next/script';

function ARViewerContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [arAssetUrl, setArAssetUrl] = useState<string>('');
  const [productInfo, setProductInfo] = useState<any>(null);
  const [modelLoaded, setModelLoaded] = useState(false);

  const token = searchParams.get('token');
  const productId = searchParams.get('product');
  const assetUrl = searchParams.get('asset');

  useEffect(() => {
    if (assetUrl) {
      // Direct asset URL provided (from product page preview)
      setArAssetUrl(assetUrl);
      setLoading(false);
    } else if (token && productId) {
      // Verify token and load AR asset
      verifyAccessAndLoadAsset();
    } else {
      setError('AR 체험을 위한 정보가 부족합니다.');
      setLoading(false);
    }
  }, [token, productId, assetUrl]);

  async function verifyAccessAndLoadAsset() {
    try {
      setLoading(true);
      setError(null);

      // Verify AR access token with custom Shopify app
      const response = await fetch(`${process.env.NEXT_PUBLIC_SHOPIFY_APP_URL}/api/ar-access/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          productId
        })
      });

      if (!response.ok) {
        throw new Error('AR 액세스 권한이 없거나 토큰이 만료되었습니다.');
      }

      const data = await response.json();

      if (!data.valid) {
        throw new Error('유효하지 않은 AR 액세스 토큰입니다.');
      }

      setArAssetUrl(data.arAssetUrl);
      setProductInfo(data.productInfo);
    } catch (err: any) {
      console.error('Error verifying AR access:', err);
      setError(err.message || 'AR 액세스 검증에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }

  function handleModelLoad() {
    setModelLoaded(true);
  }

  function handleModelError(e: any) {
    console.error('Model load error:', e);
    setError('3D 모델 로딩에 실패했습니다.');
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-center text-white">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto"></div>
          <p className="mt-4">AR 체험 준비 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900 px-4">
        <div className="text-center max-w-md">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">AR 체험 불가</h2>
          <p className="text-gray-300 mb-6">{error}</p>
          <button
            onClick={() => router.back()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            돌아가기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-black bg-opacity-50 backdrop-blur-sm border-b border-gray-700">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Cube className="w-6 h-6 text-purple-400" />
              <div>
                <h1 className="font-bold">AR 체험</h1>
                {productInfo && (
                  <p className="text-sm text-gray-400">{productInfo.title}</p>
                )}
              </div>
            </div>
            <button
              onClick={() => router.back()}
              className="text-gray-400 hover:text-white"
            >
              닫기
            </button>
          </div>
        </div>
      </div>

      {/* AR Viewer */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Model Viewer */}
          <div className="relative bg-gray-800 rounded-lg overflow-hidden mb-6" style={{ height: '600px' }}>
            {!modelLoaded && (
              <div className="absolute inset-0 flex items-center justify-center z-10">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
                  <p className="mt-4 text-gray-400">3D 모델 로딩 중...</p>
                </div>
              </div>
            )}

            {/* Using model-viewer web component for AR */}
            <model-viewer
              src={arAssetUrl}
              alt="AR Product Model"
              ar
              ar-modes="webxr scene-viewer quick-look"
              camera-controls
              auto-rotate
              style={{ width: '100%', height: '100%' }}
              onLoad={handleModelLoad}
              onError={handleModelError}
            >
              <button
                slot="ar-button"
                className="absolute bottom-4 left-1/2 transform -translate-x-1/2 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-semibold flex items-center space-x-2"
              >
                <Cube className="w-5 h-5" />
                <span>AR로 보기</span>
              </button>
            </model-viewer>
          </div>

          {/* Controls & Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Instructions */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="font-bold mb-3 flex items-center">
                <Info className="w-5 h-5 mr-2 text-blue-400" />
                사용 방법
              </h3>
              <ul className="space-y-2 text-sm text-gray-300">
                <li className="flex items-start">
                  <span className="text-purple-400 mr-2">•</span>
                  <span>마우스로 드래그하여 모델을 회전시킬 수 있습니다</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-400 mr-2">•</span>
                  <span>스크롤하여 확대/축소할 수 있습니다</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-400 mr-2">•</span>
                  <span>'AR로 보기' 버튼을 눌러 실제 공간에 배치해보세요</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-400 mr-2">•</span>
                  <span>AR 모드는 지원되는 모바일 기기에서만 사용 가능합니다</span>
                </li>
              </ul>
            </div>

            {/* Device Requirements */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="font-bold mb-3 flex items-center">
                <Cube className="w-5 h-5 mr-2 text-purple-400" />
                AR 지원 기기
              </h3>
              <div className="space-y-3 text-sm text-gray-300">
                <div>
                  <p className="font-medium text-white mb-1">iOS</p>
                  <p>iOS 12+ 및 AR Quick Look 지원 기기</p>
                </div>
                <div>
                  <p className="font-medium text-white mb-1">Android</p>
                  <p>ARCore 지원 Android 기기</p>
                </div>
                <div>
                  <p className="font-medium text-white mb-1">데스크톱</p>
                  <p>3D 모델 뷰어로 사용 가능 (AR 기능 제외)</p>
                </div>
              </div>
            </div>
          </div>

          {/* Product Info */}
          {productInfo && (
            <div className="mt-6 bg-gray-800 rounded-lg p-6">
              <h3 className="font-bold text-xl mb-2">{productInfo.title}</h3>
              <p className="text-gray-400 mb-4">{productInfo.description}</p>
              <div className="flex items-center justify-between">
                <div className="text-2xl font-bold text-purple-400">
                  ${productInfo.price}
                </div>
                {productInfo.apecLimited && (
                  <span className="px-3 py-1 bg-red-600 text-white text-sm rounded-full">
                    APEC 한정판
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Footer */}
          <div className="mt-6 text-center text-sm text-gray-500">
            <p>
              AR 체험은 구매 확인 후 90일간 이용 가능합니다
            </p>
            <p className="mt-2">
              문제가 발생하시나요?{' '}
              <a href="/support" className="text-purple-400 hover:underline">
                고객 지원팀에 문의하기
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ARViewerPage() {
  return (
    <>
      {/* Load model-viewer library */}
      <Script
        type="module"
        src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"
      />

      <Suspense fallback={
        <div className="min-h-screen flex items-center justify-center bg-gray-900">
          <div className="text-center text-white">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto"></div>
            <p className="mt-4">Loading...</p>
          </div>
        </div>
      }>
        <ARViewerContent />
      </Suspense>
    </>
  );
}
