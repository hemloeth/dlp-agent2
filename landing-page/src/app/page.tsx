'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
    ShieldCheck,
    Lock,
    Search,
    FileText,
    Download,
    ArrowRight,
    Fingerprint,
    Activity,
    Zap
} from 'lucide-react';

const Logo = () => (
    <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="logo-container"
    >
        <img
            src="/GTIS LOGO.png"
            alt="GTIS Logo"
            className="gtis-logo-img"
            style={{ height: '70px', width: 'auto', display: 'block' }}
        />
    </motion.div>
);

const FloatingCard = ({ icon: Icon, title, desc, delay, x, y }: {
    icon: React.ElementType,
    title: string,
    desc: string,
    delay: number,
    x: string,
    y: string | number
}) => (
    <motion.div
        className="floating-element"
        style={{ left: x, top: y }}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{
            opacity: 1,
            scale: 1,
            y: [0, -20, 0],
            rotate: [0, 2, -2, 0]
        }}
        transition={{
            y: {
                duration: 4 + Math.random() * 2,
                repeat: Infinity,
                ease: "easeInOut",
                delay: delay
            },
            rotate: {
                duration: 5 + Math.random() * 2,
                repeat: Infinity,
                ease: "easeInOut",
                delay: delay
            },
            opacity: { duration: 0.8, delay: delay }
        }}
        whileHover={{ scale: 1.05, zIndex: 50, transition: { duration: 0.2 } }}
    >
        <div className="floating-icon">
            <Icon size={24} />
        </div>
        <div className="floating-title">{title}</div>
        <div className="floating-desc">{desc}</div>
    </motion.div>
);

const AntigravityAnimation = () => {
    return (
        <div className="antigravity-container">
            <FloatingCard
                icon={ShieldCheck}
                title="Endpoint Guard"
                desc="Real-time PII monitoring"
                delay={0}
                x="10%"
                y="15%"
            />
            <FloatingCard
                icon={Fingerprint}
                title="Aadhaar Scan"
                desc="Deep identity detection"
                delay={0.5}
                x="50%"
                y="10%"
            />
            <FloatingCard
                icon={Lock}
                title="Privacy First"
                desc="Local data processing"
                delay={1}
                x="20%"
                y="55%"
            />
            <FloatingCard
                icon={Activity}
                title="Live Discovery"
                desc="99.8% detection rate"
                delay={1.5}
                x="60%"
                y="45%"
            />
            <FloatingCard
                icon={Zap}
                title="Fast Scan"
                desc="Turbocharged engine"
                delay={2}
                x="35%"
                y="35%"
            />
        </div>
    );
};

export default function Home() {
    return (
        <main className="main">
            <div className="container">
                <nav>
                    <Logo />
                   
                </nav>

                <section className="hero-section">
                    <motion.div
                        className="hero-content"
                        initial={{ opacity: 0, x: -30 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.8, ease: "easeOut" }}
                    >
                        <div className="badge">
                            <Activity size={14} style={{ marginRight: '8px' }} />
                            Next-Gen DLP Discovery
                        </div>
                        <h1>The Future of <span>Data Security</span></h1>
                        <p>
                            GTIS Enterprise DLP Scanner allows organizations to scan endpoints for
                            sensitive PII data like Aadhaar and PAN cards locally, ensuring Zero
                            Trust security.
                        </p>
                        <div className="cta-group">
                            <motion.a
                                href="/DLPScanner.exe"
                                className="btn btn-primary"
                                download
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                            >
                                <Download size={20} />
                                Download for Windows
                            </motion.a>
                            <motion.button
                                className="btn btn-outline"
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                            >
                                Watch Demo
                                <ArrowRight size={20} />
                            </motion.button>
                        </div>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 1, delay: 0.5 }}
                    >
                        <AntigravityAnimation />
                    </motion.div>
                </section>
            </div>


        </main>
    );
}
