import { Suspense, useEffect, useState, useRef } from 'react'
import { Canvas, useThree } from '@react-three/fiber'
import { OrbitControls, Center, GizmoHelper, GizmoViewport } from '@react-three/drei'
import * as THREE from 'three'
import { STLLoader } from 'three-stdlib'

interface ViewerProps {
  stlUrl: string
}

function StlModel({ stlUrl }: { stlUrl: string }) {
  const [geometry, setGeometry] = useState<THREE.BufferGeometry | null>(null)

  useEffect(() => {
    const loader = new STLLoader()
    loader.load(stlUrl, (geo) => {
      geo.computeVertexNormals()
      setGeometry(geo)
    })
  }, [stlUrl])

  if (!geometry) return null

  return (
    <Center>
      <mesh geometry={geometry}>
        <meshStandardMaterial color="#bfbfbf" metalness={0.4} roughness={0.6} />
      </mesh>
    </Center>
  )
}

const viewButtons = [
  { label: 'Top', position: [0, 150, 0] as [number, number, number] },
  { label: 'Front', position: [0, 0, 150] as [number, number, number] },
  { label: 'Right', position: [150, 0, 0] as [number, number, number] },
  { label: 'Iso', position: [100, 100, 100] as [number, number, number] },
]

export function Viewer({ stlUrl }: ViewerProps) {
  const [cameraTarget, setCameraTarget] = useState<[number, number, number] | null>(null)

  return (
    <div className="relative w-full h-full">
      <Canvas camera={{ position: [100, 100, 100], fov: 45 }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 10]} intensity={1} />
        <directionalLight position={[-10, -5, -10]} intensity={0.3} />
        <Suspense fallback={null}>
          <StlModel stlUrl={stlUrl} />
        </Suspense>
        <OrbitControls enableDamping dampingFactor={0.1} />
        <gridHelper args={[200, 20, '#ddd', '#eee']} />
        <GizmoHelper alignment="bottom-right" margin={[60, 60]}>
          <GizmoViewport labelColor="white" axisHeadScale={1} />
        </GizmoHelper>
        {cameraTarget && <CameraAnimator target={cameraTarget} onDone={() => setCameraTarget(null)} />}
      </Canvas>

      {/* View buttons */}
      <div className="absolute top-3 right-3 flex flex-col gap-1">
        {viewButtons.map((v) => (
          <button
            key={v.label}
            onClick={() => setCameraTarget(v.position)}
            className="px-2 py-1 text-[10px] font-medium bg-white/90 border border-neutral-200 rounded text-neutral-600 hover:bg-neutral-100 transition-colors"
          >
            {v.label}
          </button>
        ))}
      </div>
    </div>
  )
}

function CameraAnimator({ target, onDone }: { target: [number, number, number]; onDone: () => void }) {
  const { camera } = useThree()

  useEffect(() => {
    const start = camera.position.clone()
    const end = new THREE.Vector3(...target)
    let t = 0
    const animate = () => {
      t += 0.05
      if (t >= 1) {
        camera.position.copy(end)
        camera.lookAt(0, 0, 0)
        onDone()
        return
      }
      camera.position.lerpVectors(start, end, t)
      camera.lookAt(0, 0, 0)
      requestAnimationFrame(animate)
    }
    animate()
  }, [target, camera, onDone])

  return null
}
