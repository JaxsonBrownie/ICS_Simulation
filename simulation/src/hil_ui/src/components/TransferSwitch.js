import React, { useState, useEffect } from 'react';

function TransferSwitch(props) {
  // get environment variables
  //const apiUrl = process.env.REACT_APP_ENDPOINT;
  const apiUrl = props.apiUrl;

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
  console.log(data.ts_state)
  return (
    <div>
      <h3>Transfer Switch Status: {data.ts_state ? "Solar Panel" : "Mains Power"}</h3>
    </div>
  );
}

export default TransferSwitch;
