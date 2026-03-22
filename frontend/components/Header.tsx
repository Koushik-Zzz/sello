"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useTransitionPathname } from "@/context/TransitionPathnameContext";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Box, Package, Image as ImageIcon, Boxes, Edit } from "lucide-react";
import { cn } from "@/lib/utils";
import { Bungee } from "next/font/google";

const bungee = Bungee({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-bungee",
});

export function Header() {
  const pathname = useTransitionPathname();
  
  const shouldShowHeader = pathname && pathname !== "/";

  const navItems = [
    { 
      path: "/product", 
      label: "3D Product", 
      icon: Box,
      // Use Edit icon if not active?
      inactiveIcon: Edit 
    }
  ];

  return (
    <></>
  );
}
