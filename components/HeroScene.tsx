'use client'

import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Environment, MeshTransmissionMaterial, PerformanceMonitor } from '@react-three/drei'
import * as THREE from 'three'

interface LiquidChromeTorusProps {
  mousePosition: { x: number; y: number }
}

function LiquidChromeTorus({ mousePosition }: LiquidChromeTorusProps) {
  const meshRef = useRef<THREE.Mesh>(null)
  const materialRef = useRef<any>(null)

  // Create the torus knot geometry
  const geometry = useMemo(() => {
    return new THREE.TorusKnotGeometry(1.2, 0.4, 128, 32)
  }, [])

  useFrame((state) => {
    if (!meshRef.current) return
    
    // Slow rotation
    meshRef.current.rotation.x = state.clock.elapsedTime * 0.1
    meshRef.current.rotation.y = state.clock.elapsedTime * 0.15
    
    // Mouse interaction - subtle tilt
    const targetRotationX = mousePosition.y * 0.3
    const targetRotationY = mousePosition.x * 0.3
    
    meshRef.current.rotation.x += THREE.MathUtils.lerp(0, targetRotationX, 0.05)
    meshRef.current.rotation.y += THREE.MathUtils.lerp(0, targetRotationY, 0.05)
    
    // Floating animation
    meshRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
  })

  return (
    <mesh ref={meshRef} geometry={geometry} scale={0.8}>
      <MeshTransmissionMaterial
        ref={materialRef}
        transmission={1}
        thickness={2}
        roughness={0.1}
        ior={1.5}
        chromaticAberration={0.05}
        anisotropy={0.3}
        distortion={0.2}
        distortionScale={0.5}
        temporalDistortion={0.1}
        color="#F43F5E"
        attenuationColor="#E11D48"
        attenuationDistance={1}
      />
    </mesh>
  )
}

function Scene({ mousePosition }: { mousePosition: { x: number; y: number } }) {
  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#F43F5E" />
      <LiquidChromeTorus mousePosition={mousePosition} />
      <Environment preset="studio" />
    </>
  )
}

interface HeroSceneProps {
  mousePosition: { x: number; y: number }
}

export default function HeroScene({ mousePosition }: HeroSceneProps) {
  const [dpr, setDpr] = React.useState(1.5)

  return (
    <div className="absolute inset-0 z-0">
      <PerformanceMonitor onDecline={() => setDpr(1)}>
        <Canvas
          dpr={dpr}
          camera={{ position: [0, 0, 5], fov: 45 }}
          gl={{ antialias: true, alpha: true }}
          style={{ background: 'transparent' }}
        >
          <Scene mousePosition={mousePosition} />
        </Canvas>
      </PerformanceMonitor>
    </div>
  )
}
