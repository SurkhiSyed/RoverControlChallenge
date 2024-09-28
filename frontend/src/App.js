import logo from './logo.svg';
import './App.css';
import WheelDisplay from './components/displayInfo';
import * as THREE from 'three';
import { useEffect } from 'react';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import Stats from 'three/examples/jsm/libs/stats.module';

function App() {
  useEffect(() => {
    // Create the scene
    const scene = new THREE.Scene();
  
    // Set the background color to white
    scene.background = new THREE.Color(0xffffff); // White background
  
    // Set up the camera
    const camera = new THREE.PerspectiveCamera(
      50, 
      window.innerWidth / window.innerHeight, 
      1, 
      1000
    );
    camera.position.z = 96;
  
    // Set up the renderer
    const canvas = document.getElementById('myThreeJsCanvas');
    const renderer = new THREE.WebGLRenderer({ 
      canvas,
      antialias: true,
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);
  
    // Add ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    ambientLight.castShadow = true;
    scene.add(ambientLight);
  
    // Add spotlight
    const spotLight = new THREE.SpotLight(0xffffff, 1);
    spotLight.castShadow = true;
    spotLight.position.set(0, 64, 32);
    scene.add(spotLight);
  
    // Create the Rover (main body and wheels)
  
    // Main Rover Body (BoxGeometry)
    const bodyGeometry = new THREE.BoxGeometry(24, 8, 20);
    const bodyMaterial = new THREE.MeshNormalMaterial(); // Use a normal material
    const roverBody = new THREE.Mesh(bodyGeometry, bodyMaterial);
    scene.add(roverBody);
  
    // Wheels (TorusGeometry for hollow and spokes using CylinderGeometry)
    const wheelOuterGeometry = new THREE.TorusGeometry(4, 1, 16, 100); // Hollow torus shape
    const wheelMaterial = new THREE.MeshLambertMaterial({ color: 0x333333 });
  
    for (let i = 0; i < 4; i++) {
      // Create the hollow wheel (torus)
      const wheel = new THREE.Mesh(wheelOuterGeometry, wheelMaterial);
      //wheel.rotation.x = Math.PI / 2; // Rotate the wheel to lay flat
  
      const xOffset = i < 2 ? -10 : 10; // X position (left-right)
      const zOffset = i % 2 === 0 ? 12 : -12; // Z position (front-back)
      const yOffset = -6; // Y position (under the body)
      wheel.position.set(xOffset, yOffset, zOffset);
      roverBody.add(wheel); // Attach wheels to the rover body
  
      // Create spokes for the wheel
      const spokeGeometry = new THREE.CylinderGeometry(0.2, 0.2, 8, 32);
      for (let j = 0; j < 6; j++) {
        const spoke = new THREE.Mesh(spokeGeometry, wheelMaterial);
        spoke.position.set(0, 0, 0); // Center the spoke in the wheel
        spoke.rotation.z = (Math.PI / 3) * j; // Rotate the spokes evenly
        wheel.add(spoke);
      }
    }
  
    // Orbit Controls
    const controls = new OrbitControls(camera, renderer.domElement);
  
    // Stats
    const stats = Stats();
    document.body.appendChild(stats.dom);
  
    // Animation loop
    const animate = () => {
      stats.update();
      controls.update();
      renderer.render(scene, camera);
      window.requestAnimationFrame(animate);
    };
  
    animate();
  }, []);
  

  
  return (
    <div className="App">
      <div>
      <canvas id="myThreeJsCanvas" />
      </div>
      <WheelDisplay />
      <h1>Hello</h1>
    </div>
  );
}

export default App;
