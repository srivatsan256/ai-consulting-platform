import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva } from "class-variance-authority"
import { cn } from "@/lib/utils"
import "../../styles/components/ui/button.css";

const buttonVariants = cva(
  "ui-btn",
  {
    variants: {
      variant: {
        default: "ui-btn-default text-primary-foreground",
        destructive: "ui-btn-destructive",
        outline: "ui-btn-outline",
        secondary: "ui-btn-secondary text-secondary-foreground",
        ghost: "ui-btn-ghost",
        link: "ui-btn-link",
      },
      size: {
        default: "ui-btn-size-default",
        sm: "ui-btn-sm",
        lg: "ui-btn-lg",
        icon: "ui-btn-icon",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
)

const Button = React.forwardRef(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  },
)
Button.displayName = "Button"

export { Button, buttonVariants }
