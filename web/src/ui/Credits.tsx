import { useState } from 'react'

const CREDITS = [
  'Bride character: White Wedding Dress Girl by FERUL (CGTrader). Motion: Microsoft Rocketbox (MIT).',
]

/** A small Credits button that opens a panel listing the assets' authors. */
export function Credits() {
  const [open, setOpen] = useState(false)
  return (
    <>
      <button onClick={() => setOpen(true)}>Credits</button>
      {open && (
        <div className="credits" role="dialog" aria-label="Credits" onClick={() => setOpen(false)}>
          <div className="credits-panel" onClick={(e) => e.stopPropagation()}>
            <h2>Credits</h2>
            {CREDITS.map((line) => (
              <p key={line}>{line}</p>
            ))}
            <button onClick={() => setOpen(false)}>Close</button>
          </div>
        </div>
      )}
    </>
  )
}
