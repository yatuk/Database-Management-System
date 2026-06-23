import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface BarChartProps {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string;
  }[];
  title?: string;
  horizontal?: boolean;
}

export default function BarChart({ labels, datasets, title, horizontal }: BarChartProps) {
  const data = { labels, datasets };
  const options = {
    indexAxis: horizontal ? ("y" as const) : ("x" as const),
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: "bottom" as const },
      title: title ? { display: true, text: title, font: { size: 16 } } : undefined,
    },
  };

  return (
    <div className="w-full h-80">
      <Bar data={data} options={options} />
    </div>
  );
}
