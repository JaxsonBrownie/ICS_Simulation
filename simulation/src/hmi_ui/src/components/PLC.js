function PLC(props) {
  // pass props
  let holding_regs = props.hr
  let coils = props.coil

  // render
  return (
    <div>
      <b>Current solar panel power meter reading: {holding_regs[0]}</b>
      <br></br>
      <b>Switching threshold (mW): {holding_regs[1]}</b>
      <br></br>
      <b>Current input power: {coils ? "Solar Panel Power" : "Mains Power"}</b> 
    </div>
  );
}

export default PLC;
