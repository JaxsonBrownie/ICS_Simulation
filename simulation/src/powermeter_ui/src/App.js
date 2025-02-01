import React, { useState, useEffect } from 'react';

function App() {
  // get environment variables
  const apiUrl = process.env.REACT_APP_ENDPOINT;

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
  }, [])

  /*
  Function: calcTime
  Purpose: Takes in the total amount of minutes that have passed and
    formats it into HR:MN
  */
  const calcTime = (totalMinutes) => {
    let hours = Math.floor(totalMinutes / 60) % 24;
    hours = hours < 10 ? `0${hours}` : hours;
    
    let minutes = totalMinutes % 60;
    minutes = minutes < 10 ? `0${minutes}` : minutes;
  
    return { hours, minutes };
  }

  // render loading or error
  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}. Simulation may be offline</p>;

  // calculate time
  const formatTime = calcTime(data.time);
  const hour = formatTime.hours;
  const minute = formatTime.minutes;

  let dayCycle = "";

  // calculate day cycle
  if (hour < 6) {
    dayCycle = "Morning"
  } else if (hour < 12) {
    dayCycle = "Day"
  } else if (hour < 18) {
    dayCycle = "Afternoon"
  } else {
    dayCycle = "Night"
  }
  
  // render
  return (
    <div>
      <h3>Time: {hour}:{minute}</h3>
      <h3>Current Day Cycle: {dayCycle}</h3>
      <br></br>
      <h3>Power Meter Reading: {data.pm_reading}</h3>
    </div>
  );
}

export default App;
