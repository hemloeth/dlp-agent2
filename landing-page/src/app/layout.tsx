import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
    title: 'DLP Scanner | Ultimate Security for your Data',
    description: 'Download the most advanced DLP scanner to protect your sensitive information from leaking.',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <head>
                <link rel="preconnect" href="https://fonts.googleapis.com" />
                <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet" />
            </head>
            <body>{children}</body>
        </html>
    )
}
