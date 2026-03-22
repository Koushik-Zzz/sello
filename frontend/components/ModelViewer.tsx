"use client";

import React, { useRef, Suspense, useEffect, useMemo } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment, useGLTF } from "@react-three/drei";
import { OrbitControls as OrbitControlsImpl } from "three-stdlib";
import * as THREE from "three";

export interface ModelViewerRef {
  captureScreenshot: () => Promise<string>;
}

interface ModelViewerProps {
  modelUrl?: string;
  error?: string | null;
  lightingMode?: "studio" | "sunset" | "warehouse" | "forest";
  wireframe?: boolean;
  zoomAction?: "in" | "out" | null;
  autoRotate?: boolean;
}

function ModelLoader({
  url,
  wireframe,
  opacity,
  onLoad,
}: {
  url: string;
  wireframe: boolean;
  opacity: number;
  onLoad?: () => void;
}) {
  const { scene } = useGLTF(url);
  const clonedScene = useMemo(() => {
    const cloned = scene.clone(true);

    // Clone mesh materials to avoid mutating shared GLTF cache instances.
    cloned.traverse((child) => {
      if (child instanceof THREE.Mesh && child.material) {
        if (Array.isArray(child.material)) {
          child.material = child.material.map((mat) => mat.clone());
        } else {
          child.material = child.material.clone();
        }
      }
    });

    // Normalize model transform so very large/small or off-origin assets stay visible.
    const box = new THREE.Box3().setFromObject(cloned);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);

    if (Number.isFinite(maxDim) && maxDim > 0) {
      const targetSize = 2.2;
      const scale = targetSize / maxDim;
      cloned.scale.setScalar(scale);
      cloned.position.set(-center.x * scale, -center.y * scale, -center.z * scale);
    }

    return cloned;
  }, [scene, url]);

  useEffect(() => {
    clonedScene.traverse((child) => {
      if (child instanceof THREE.Mesh && child.material) {
        const materials = Array.isArray(child.material) ? child.material : [child.material];

        materials.forEach((material) => {
          if (material instanceof THREE.MeshStandardMaterial || material instanceof THREE.MeshPhysicalMaterial) {
            // Preserve base material values so we can restore when leaving wireframe mode.
            if (!material.userData.__baseColor) {
              material.userData.__baseColor = material.color.clone();
            }
            if (!material.userData.__baseEmissive) {
              material.userData.__baseEmissive = material.emissive.clone();
            }
            if (material.userData.__baseEmissiveIntensity === undefined) {
              material.userData.__baseEmissiveIntensity = material.emissiveIntensity;
            }

            material.wireframe = wireframe;
            material.opacity = opacity;
            material.transparent = opacity < 1;
            material.needsUpdate = true;

            if (wireframe) {
              material.emissive = new THREE.Color("#60a5fa");
              material.emissiveIntensity = 0.2;
              material.color = new THREE.Color("#60a5fa");
            } else {
              material.color.copy(material.userData.__baseColor);
              material.emissive.copy(material.userData.__baseEmissive);
              material.emissiveIntensity = material.userData.__baseEmissiveIntensity;
            }
          }
        });
      }
    });
  }, [clonedScene, wireframe, opacity]);

  useEffect(() => {
    onLoad?.();
  }, [onLoad]);

  return <primitive object={clonedScene} />;
}

function ModelLoaderWrapper({ url, wireframe }: { url: string; wireframe: boolean }) {
  return (
    <Suspense fallback={null}>
      <ModelLoader url={url} wireframe={wireframe} opacity={1} onLoad={() => {}} />
    </Suspense>
  );
}

function ErrorDisplay({ message }: { message: string }) {
  return (
    <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
      <div className="text-center px-8">
        <div className="mb-4">
          <svg
            className="w-16 h-16 text-red-500 mx-auto"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <p className="text-red-400 text-lg font-semibold mb-2">Error</p>
        <p className="text-gray-400 text-sm">{message}</p>
      </div>
    </div>
  );
}

const ModelViewer = React.forwardRef<ModelViewerRef, ModelViewerProps>(
  function ModelViewer({
    modelUrl,
    error,
    lightingMode = "studio",
    wireframe = false,
    zoomAction,
    autoRotate = true,
  }, ref) {
  const controlsRef = useRef<OrbitControlsImpl>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Expose screenshot function via ref
  React.useImperativeHandle(ref, () => ({
    captureScreenshot: async () => {
      if (!canvasRef.current) {
        throw new Error("Canvas not available");
      }
      
      // Get the canvas element
      const canvas = canvasRef.current;
      
      // Convert to blob then to data URL for better quality
      return new Promise<string>((resolve, reject) => {
        canvas.toBlob((blob) => {
          if (!blob) {
            reject(new Error("Failed to capture screenshot"));
            return;
          }
          
          const reader = new FileReader();
          reader.onloadend = () => {
            resolve(reader.result as string);
          };
          reader.onerror = reject;
          reader.readAsDataURL(blob);
        }, "image/jpeg", 0.95);
      });
    },
  }), []);

  useEffect(() => {
    if (!zoomAction || !controlsRef.current) return;

    const currentDistance = controlsRef.current.getDistance();
    const newDistance = zoomAction === "in" 
      ? Math.max(currentDistance * 0.8, 2) 
      : Math.min(currentDistance * 1.2, 10);

    controlsRef.current.minDistance = newDistance;
    controlsRef.current.maxDistance = newDistance;
    controlsRef.current.update();

    const timer = setTimeout(() => {
      if (controlsRef.current) {
        controlsRef.current.minDistance = 2;
        controlsRef.current.maxDistance = 10;
      }
    }, 100);

    return () => clearTimeout(timer);
  }, [zoomAction]);

  // Don't render Canvas until we have a model URL to prevent WebGL context starvation
  if (!modelUrl && !error) {
    return <div className="w-full h-full relative overflow-hidden bg-muted/30" />;
  }

  return (
    <div className="w-full h-full relative overflow-hidden">
      <Canvas
        key="product-viewer-canvas"
        camera={{ position: [2, 1.5, 3.5], fov: 50 }}
        gl={{
          toneMapping: 2,
          toneMappingExposure: 2.0,
          preserveDrawingBuffer: true, // Enable for screenshot capture
          powerPreference: "high-performance",
          antialias: true,
        }}
        className="w-full h-full"
        frameloop="always"
        onCreated={({ gl }) => {
          canvasRef.current = gl.domElement;
        }}
      >
        <color attach="background" args={["#ffffff"]} />

        <Suspense fallback={null}>
          <Environment preset={lightingMode} background={false} />
          <ambientLight intensity={1.5} />
          <directionalLight position={[5, 5, 5]} intensity={2.4} castShadow />
          <directionalLight position={[-5, 3, -5]} intensity={0.9} />

          {modelUrl && <ModelLoaderWrapper url={modelUrl} wireframe={wireframe} />}

          <OrbitControls
            ref={controlsRef}
            enableDamping
            dampingFactor={0.05}
            minDistance={2}
            maxDistance={10}
            autoRotate={autoRotate}
            autoRotateSpeed={1.5}
          />
        </Suspense>
      </Canvas>

      {error && <ErrorDisplay message={error} />}
    </div>
  );
});

export default ModelViewer;
