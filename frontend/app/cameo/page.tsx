'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Video,
  Upload,
  Wand2,
  Download,
  Share2,
  CheckCircle,
  Loader2,
  User,
  MessageSquare,
  Calendar,
} from 'lucide-react';
import CAMEOCreator from '@/components/CAMEOCreator';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';

interface CAMEORequest {
  occasion: string;
  recipientName: string;
  personalMessage: string;
  selectedProducts: string[];
  tone: string;
  deliveryDate?: string;
}

interface CAMEOVideo {
  id: string;
  video_url: string;
  thumbnail_url: string;
  status: 'processing' | 'completed' | 'failed';
  created_at: string;
  request: CAMEORequest;
}

export default function CAMEOPage() {
  const [currentStep, setCurrentStep] = useState<'create' | 'preview' | 'complete'>('create');
  const [cameoVideo, setCAMEOVideo] = useState<CAMEOVideo | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleCreateCAMEO = async (request: CAMEORequest) => {
    try {
      setIsGenerating(true);
      toast.loading('Generating your personalized CAMEO video...', { duration: 3000 });

      const response = await api.post('/cameo/generate', {
        occasion: request.occasion,
        recipient_name: request.recipientName,
        personal_message: request.personalMessage,
        product_ids: request.selectedProducts,
        tone: request.tone,
        delivery_date: request.deliveryDate,
      });

      setCAMEOVideo(response.data);
      setCurrentStep('preview');
      toast.success('CAMEO video generated successfully!');
    } catch (error) {
      console.error('Failed to generate CAMEO:', error);
      toast.error('Failed to generate CAMEO video. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = async () => {
    if (!cameoVideo) return;

    try {
      const response = await fetch(cameoVideo.video_url);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `cameo-${cameoVideo.id}.mp4`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast.success('Video downloaded successfully!');
    } catch (error) {
      console.error('Failed to download video:', error);
      toast.error('Failed to download video');
    }
  };

  const handleShare = async () => {
    if (!cameoVideo) return;

    if (navigator.share) {
      try {
        await navigator.share({
          title: 'My Personalized CAMEO Video',
          text: 'Check out this personalized video message!',
          url: cameoVideo.video_url,
        });
        toast.success('Shared successfully!');
      } catch (error) {
        console.error('Failed to share:', error);
      }
    } else {
      // Fallback: Copy link to clipboard
      navigator.clipboard.writeText(cameoVideo.video_url);
      toast.success('Link copied to clipboard!');
    }
  };

  const handleCreateAnother = () => {
    setCurrentStep('create');
    setCAMEOVideo(null);
  };

  return (
    <div className="min-h-screen gradient-bg">
      <div className="section-container">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 bg-secondary-100 text-secondary-700 px-4 py-2 rounded-full text-sm font-semibold mb-4">
            <Wand2 className="w-4 h-4" />
            <span>AI-Powered Video Generation</span>
          </div>

          <h1 className="text-5xl font-bold mb-4">
            Create Your <span className="text-gradient">CAMEO</span> Video
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Get a personalized video message from Sam Altman showcasing your selected products.
            Perfect for gifts, special occasions, or just making someone smile!
          </p>
        </motion.div>

        {/* Progress Steps */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="max-w-3xl mx-auto mb-12"
        >
          <div className="flex items-center justify-between">
            {[
              { id: 'create', label: 'Create', icon: Video },
              { id: 'preview', label: 'Preview', icon: Upload },
              { id: 'complete', label: 'Complete', icon: CheckCircle },
            ].map((step, index) => (
              <div key={step.id} className="flex items-center flex-1">
                <div
                  className={`flex items-center gap-3 ${
                    currentStep === step.id
                      ? 'text-primary-600'
                      : index < ['create', 'preview', 'complete'].indexOf(currentStep)
                      ? 'text-primary-600'
                      : 'text-gray-400'
                  }`}
                >
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center font-semibold ${
                      currentStep === step.id
                        ? 'bg-primary-600 text-white'
                        : index < ['create', 'preview', 'complete'].indexOf(currentStep)
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-200 text-gray-400'
                    }`}
                  >
                    <step.icon className="w-6 h-6" />
                  </div>
                  <span className="font-semibold hidden sm:inline">{step.label}</span>
                </div>
                {index < 2 && (
                  <div
                    className={`flex-1 h-1 mx-4 ${
                      index < ['create', 'preview', 'complete'].indexOf(currentStep)
                        ? 'bg-primary-600'
                        : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </motion.div>

        {/* Content */}
        {currentStep === 'create' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <CAMEOCreator
              onSubmit={handleCreateCAMEO}
              isLoading={isGenerating}
            />
          </motion.div>
        )}

        {currentStep === 'preview' && cameoVideo && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="max-w-4xl mx-auto"
          >
            <div className="card">
              <div className="grid md:grid-cols-2 gap-8">
                {/* Video Preview */}
                <div>
                  <h3 className="text-xl font-bold mb-4">Your CAMEO Video</h3>
                  {cameoVideo.status === 'processing' ? (
                    <div className="cameo-preview bg-gray-200 flex flex-col items-center justify-center">
                      <Loader2 className="w-12 h-12 text-primary-600 animate-spin mb-4" />
                      <p className="text-gray-600">Processing your video...</p>
                    </div>
                  ) : cameoVideo.status === 'completed' ? (
                    <video
                      src={cameoVideo.video_url}
                      poster={cameoVideo.thumbnail_url}
                      controls
                      className="w-full cameo-preview"
                    />
                  ) : (
                    <div className="cameo-preview bg-red-50 flex flex-col items-center justify-center">
                      <p className="text-red-600">Failed to generate video</p>
                    </div>
                  )}

                  {cameoVideo.status === 'completed' && (
                    <div className="flex gap-3 mt-4">
                      <button
                        onClick={handleDownload}
                        className="btn-primary flex-1 flex items-center justify-center gap-2"
                      >
                        <Download className="w-5 h-5" />
                        <span>Download</span>
                      </button>
                      <button
                        onClick={handleShare}
                        className="btn-outline flex-1 flex items-center justify-center gap-2"
                      >
                        <Share2 className="w-5 h-5" />
                        <span>Share</span>
                      </button>
                    </div>
                  )}
                </div>

                {/* Request Details */}
                <div className="space-y-6">
                  <h3 className="text-xl font-bold">Request Details</h3>

                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center gap-2 text-gray-600 mb-2">
                        <Calendar className="w-4 h-4" />
                        <span className="text-sm font-semibold">Occasion</span>
                      </div>
                      <p className="text-lg">{cameoVideo.request.occasion}</p>
                    </div>

                    <div>
                      <div className="flex items-center gap-2 text-gray-600 mb-2">
                        <User className="w-4 h-4" />
                        <span className="text-sm font-semibold">Recipient</span>
                      </div>
                      <p className="text-lg">{cameoVideo.request.recipientName}</p>
                    </div>

                    <div>
                      <div className="flex items-center gap-2 text-gray-600 mb-2">
                        <MessageSquare className="w-4 h-4" />
                        <span className="text-sm font-semibold">Message</span>
                      </div>
                      <p className="text-gray-700 bg-gray-50 p-4 rounded-lg">
                        {cameoVideo.request.personalMessage}
                      </p>
                    </div>

                    <div>
                      <div className="flex items-center gap-2 text-gray-600 mb-2">
                        <Wand2 className="w-4 h-4" />
                        <span className="text-sm font-semibold">Tone</span>
                      </div>
                      <p className="text-lg capitalize">{cameoVideo.request.tone}</p>
                    </div>
                  </div>

                  <button
                    onClick={handleCreateAnother}
                    className="btn-secondary w-full"
                  >
                    Create Another CAMEO
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Features Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-20"
        >
          <h2 className="text-3xl font-bold text-center mb-12">
            Why Choose CAMEO Videos?
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Video,
                title: 'Personalized Content',
                description:
                  'Each video is uniquely generated with your custom message and selected products',
              },
              {
                icon: Wand2,
                title: 'AI-Powered Magic',
                description:
                  'Advanced AI creates natural, engaging videos featuring Sam Altman',
              },
              {
                icon: Share2,
                title: 'Easy Sharing',
                description:
                  'Download and share your CAMEO videos across all platforms instantly',
              },
            ].map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 + index * 0.1 }}
                className="card text-center hover:shadow-xl transition-shadow duration-300"
              >
                <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <feature.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Use Cases */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mt-20 card bg-gradient-to-r from-primary-600 to-secondary-600 text-white text-center p-12"
        >
          <h2 className="text-3xl font-bold mb-6">Perfect For Every Occasion</h2>
          <div className="grid md:grid-cols-4 gap-6 text-center">
            {['Birthdays', 'Holidays', 'Anniversaries', 'Thank You'].map((occasion) => (
              <div key={occasion} className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
                <p className="text-lg font-semibold">{occasion}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
