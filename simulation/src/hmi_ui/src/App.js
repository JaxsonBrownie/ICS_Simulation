import React, { useState, useEffect } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import PLC from './components/PLC';

function App() {
  // get environment variables
  const apiUrl = process.env.REACT_APP_ENDPOINT;
  //const apiUrl = "127.0.0.1";

  // initialise state hooks
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // initialise fetch hooks
  useEffect(() => {
    const interval = setInterval(() => {
       // Fetch data from the API endpoint
      fetch(apiUrl)
      .then(response => {
        // check for errors
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        // set state data to the fetched data
        setData(data);
        setLoading(false);
      })
      .catch(error => {
        // handle errors
        setError(error);
        setLoading(false);
      });
    }, 100); // 100ms interval

    // Cleanup function to clear the interval when the component unmounts
    return () => clearInterval(interval);
  }, [apiUrl])

  // render loading or error
  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}. Simulation may be offline</p>;
  
  // render
  return (
    <div>
      <Container>
        <Row>
          <Col>
            <h2>Household 1</h2>
            <p>Consists of PLC1 and HIL1 components.</p>
            <PLC hr={data.plc1.hr} coil={data.plc1.coil[0]}/>
          </Col>
          <Col>
            <h2>Household 2</h2>
            <p>Consists of PLC2 and HIL2 components.</p>
            <PLC hr={data.plc2.hr} coil={data.plc2.coil[0]}/>
          </Col>
        </Row>
      </Container>
    </div>
  );
}

export default App;
