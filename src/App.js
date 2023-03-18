import { useState } from 'react';
import './App.css';
import Calendar from 'react-calendar'
import './Calendar.css';

function App() {
    const [pickedDate, setPickedDate] = useState(new Date());
    const [inputValue, setInputValue] = useState('');
    const [timeSlots, setTimeSlots] = useState([]);

    const handleDateChange = (date) => {
      setPickedDate(date);
    };
    

    const handleInputChange = (event) => {
      setInputValue(event.target.value);
    };
    const handleSubmit = async (e) => {
      e.preventDefault();
      const response = await fetch("http://localhost:8000/user/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ inputValue,pickedDate }),
      });
      const data = await response.json();
      console.log("recieved data",data);
      setTimeSlots(data);
    };
    const handleBookSlot = (index) => {
      console.log("Booked slot", timeSlots[index]);
    };
    console.log("Array",timeSlots)


    function TimeSlot({ start_time, end_time }) {
      return (
        <td onClick={() => console.log(`Clicked: ${start_time} - ${end_time}`)}>
          {start_time} - {end_time}
        </td>
      );
    }
    
    function TimeSlotTable({ timeSlots }) {
      const numCols = 3;
      const numRows = 5;
      const rows = [];
      for (let i = 0; i < numRows; i++) {
        const row = [];
        for (let j = 0; j < numCols; j++) {
          const index = i * numCols + j;
          if (index < timeSlots.length) {
            const { start_time, end_time } = timeSlots[index];
            row.push(<TimeSlot key={index} start_time={start_time} end_time={end_time} />);
          } else {
            row.push(<td key={j}></td>);
          }
        }
        rows.push(<tr key={i}>{row}</tr>);
      }
      return (
        <table>
          <tbody>{rows}</tbody>
        </table>
      );
    }
    return (
      <div className="App">
        <div className='calendar-card'>
        <form onSubmit={handleSubmit}>
          <div className="calendar-placing">
            <Calendar onChange={handleDateChange} value={pickedDate} />
  
            <div className="date-picked">
              <p>You picked: {pickedDate.toString()}</p>
            </div>
            <br/>
            <div className="enter-name">
              <label>
                Setup 1-1 with :
                <br />
                <input type="text" value={inputValue} onChange={handleInputChange} />
              </label>
              <br />
              <button type="submit">Submit</button>
            </div>
          </div>
        
          
          {timeSlots.length > 0 && (
              <div className="show-time-slots">
                <TimeSlotTable timeSlots={timeSlots} />
              </div>
            )}
            </form>
            </div>
      </div>
    );
  }
  
  export default App;
// import React from 'react';

// function TimeTable({ timeSlots }) {
//   return (
//     <table>
//       <thead>
//         <tr>
//           <th>Time Slot</th>
//         </tr>
//       </thead>
//       <tbody>
//         {timeSlots.map((timeSlot, index) => (
//           <tr key={index}>
//             <td>{timeSlot.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</td>
//           </tr>
//         ))}
//       </tbody>
//     </table>
//   );
// }

// export default TimeTable;