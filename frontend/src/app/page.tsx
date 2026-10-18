export default function Home() {
  return (
    <div className="flex flex-col items-center">
      {/* Hero Section */}
      <section className="w-full bg-gradient-to-br from-primary-600 to-primary-800 px-4 py-20 text-center text-white">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
          Hayat<span className="text-primary-200">Connect</span>
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-primary-100 sm:text-xl">
          Connecting patients with verified blood donors across Karachi.
          <br />
          AI-powered matching. Real-time alerts. Lives saved.
        </p>
        <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <a href="/register" className="btn-primary bg-white !text-primary-700 hover:!bg-primary-50 px-8 py-3 text-lg">
            Register as Donor
          </a>
          <a href="/requests/new" className="inline-flex items-center justify-center rounded-lg border-2 border-white bg-transparent px-8 py-3 text-lg font-semibold text-white transition hover:bg-white hover:text-primary-700">
            Request Blood
          </a>
        </div>
      </section>

      {/* How It Works */}
      <section className="w-full px-4 py-16">
        <h2 className="text-center text-3xl font-bold text-gray-900">
          How It Works
        </h2>
        <div className="mx-auto mt-12 grid max-w-5xl gap-8 sm:grid-cols-3">
          {[
            {
              step: "1",
              title: "Post a Request",
              desc: "Enter the blood group, hospital, and urgency level. Our system takes it from there.",
            },
            {
              step: "2",
              title: "AI Matches Donors",
              desc: "Smart algorithm ranks nearby eligible donors by distance, availability, and reliability.",
            },
            {
              step: "3",
              title: "Donor Responds",
              desc: "Matched donors get instant notifications and can accept with one tap.",
            },
          ].map((item) => (
            <div key={item.step} className="card text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary-100 text-xl font-bold text-primary-600">
                {item.step}
              </div>
              <h3 className="mt-4 text-lg font-semibold">{item.title}</h3>
              <p className="mt-2 text-sm text-gray-600">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Stats Placeholder */}
      <section className="w-full bg-primary-50 px-4 py-16">
        <div className="mx-auto grid max-w-4xl gap-8 text-center sm:grid-cols-3">
          {[
            { value: "0", label: "Donors Registered" },
            { value: "0", label: "Lives Connected" },
            { value: "24/7", label: "Availability" },
          ].map((stat) => (
            <div key={stat.label}>
              <p className="text-4xl font-bold text-primary-600">{stat.value}</p>
              <p className="mt-1 text-sm text-gray-600">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
