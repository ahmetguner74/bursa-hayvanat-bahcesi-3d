// Yaw in world Z after standing the XY card upright. XYZ Euler order would
// rotate its image inside the same vertical plane, creating coplanar cards.
export function orientPlantCard(object,angle){
  object.rotation.set(Math.PI/2,0,angle,'ZYX');
}
