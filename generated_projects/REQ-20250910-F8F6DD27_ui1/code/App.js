import React from 'react';

function App() {
  try {
    return <div>Hello World!</div>;
  } catch (error) {
    console.error('Error rendering component:', error);
    // Return a default value instead of null to avoid potential issues with React
    return <div>Error rendering component: {error.message}</div>;
  }
}

export default App;