import { motion } from "framer-motion";

export interface MascotProps {
  className?: string;
  animate?: boolean;
}

export function Mascot({ className, animate = true }: MascotProps) {
  return (
    <motion.div
      className={className}
      initial={animate ? { opacity: 0, y: 50, scale: 0.8 } : {}}
      animate={animate ? { 
        opacity: 1, 
        y: [0, -15, 0],
        scale: 1,
      } : {}}
      transition={{
        opacity: { duration: 1, ease: "easeOut" },
        y: { 
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut",
          repeatType: "reverse"
        },
        scale: { duration: 0.8, ease: "easeOut" }
      }}
    >
      <div className="relative">
        {/* Animated glow effect */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-full blur-xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.5, 0.8, 0.5],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        
        {/* Mascot image */}
        <motion.img 
          src="/assets/mascot.png"
          alt="LearnHub Mascot"
          className="relative z-10 w-full h-full object-contain drop-shadow-2xl brightness-105"
          animate={animate ? {
            rotate: [0, -3, 3, -3, 0],
            scale: [1, 1.02, 1],
          } : {}}
          transition={{
            rotate: {
              duration: 6,
              repeat: Infinity,
              ease: "easeInOut",
              repeatType: "reverse"
            },
            scale: {
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
              repeatType: "reverse"
            }
          }}
        />
      </div>
    </motion.div>
  );
}
