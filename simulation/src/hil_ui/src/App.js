import React from 'react'
import { Container, Row, Col } from 'react-bootstrap'
import PowerMeter from './components/PowerMeter';
import TransferSwitch from './components/TransferSwitch';

function App() {
  const powermeter_url = process.env.REACT_APP_ENDPOINT_PM;
  const transferswitch_url = process.env.REACT_APP_ENDPOINT_TS;

  return (
    <>
      <Container>
        <Row>
          <Col>
            <PowerMeter apiUrl={powermeter_url} />
          </Col>
          <Col>
            <TransferSwitch apiUrl={transferswitch_url} />
          </Col>
        </Row>
      </Container>
    </>
  );
}

export default App;
