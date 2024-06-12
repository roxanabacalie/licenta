import logo from './logo.svg';
import './App.css';
import Navbar from './hooks/Navbar/Navbar';
import HomePage from './pages/HomePage/HomePage';
import Footer from './hooks/Footer/Footer';

function App() {
  return (
    <div className="App">
      <Navbar />
      <HomePage />
      <Footer />
    </div>
  );
}

export default App;
