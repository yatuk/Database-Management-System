const MEMBERS = [
  { name: "Gulbahar Karabas", number: "150210085" },
  { name: "Salih Sefer", number: "820230313" },
  { name: "Muhammet Tuncer", number: "820230314" },
  { name: "Atahan Evintan", number: "820230334" },
  { name: "Fatih Serdar Cakmak", number: "820230326" },
];

export default function AboutPage() {
  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">About</h1>

      <div className="bg-white rounded-xl shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-2">Database Management System</h2>
        <p className="text-gray-600">
          A comprehensive web-based platform for analyzing World Development Indicators (WDI)
          data across multiple domains: Health, GHG Emissions, Energy, Freshwater, and Sustainability.
        </p>
        <p className="text-gray-500 text-sm mt-4">
          BLG-317E Database Systems - Istanbul Technical University
        </p>
      </div>

      <h2 className="text-xl font-semibold mb-4">Team Members</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {MEMBERS.map((m) => (
          <div key={m.number} className="bg-white p-4 rounded-lg shadow flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold">
              {m.name.charAt(0)}
            </div>
            <div>
              <div className="font-medium">{m.name}</div>
              <div className="text-sm text-gray-500">{m.number}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
